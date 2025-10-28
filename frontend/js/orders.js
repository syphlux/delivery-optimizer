const apiBase = "http://127.0.0.1:8000/orders/";
const ordersTableBody = document.getElementById("ordersTableBody");
const modal = document.getElementById("orderModal");
const newOrderBtn = document.getElementById("newOrderBtn");
const closeModal = document.getElementById("closeModal");
const orderForm = document.getElementById("orderForm");

let ordersData = [];
let currentSort = { key: null, asc: true };

const statusOrder = ["PENDING", "PRE_DELIVERY", "IN_ROUTE", "DELIVERED", "CANCELLED"];

function compareDates(a, b, key) {
  const dateA = new Date(a[key]);
  const dateB = new Date(b[key]);
  return dateA - dateB;
}

function compareStatus(a, b) {
  return statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status);
}

function sortOrders(key) {
  if (currentSort.key === key) {
    currentSort.asc = !currentSort.asc;
  } else {
    currentSort.key = key;
    currentSort.asc = true;
  }
  let sorted = [...ordersData];
  if (key === "available_from" || key === "deadline") {
    sorted.sort((a, b) => compareDates(a, b, key));
  } else if (key === "status") {
    sorted.sort(compareStatus);
  }
  if (!currentSort.asc) sorted.reverse();
  renderOrders(sorted);
}

async function fetchOrders() {
  try {
    const response = await fetch(apiBase);
    if (!response.ok) throw new Error("Failed to fetch orders");
    const data = await response.json();
    ordersData = data;
    renderOrders(data);
  } catch (err) {
    console.error(err);
    alert("Could not load orders.");
  }
}

function getStatusColor(status) {
  switch (status) {
    case "PENDING": return "bg-yellow-200 text-yellow-800";
    case "PRE_DELIVERY": return "bg-blue-200 text-blue-800";
    case "IN_ROUTE": return "bg-purple-200 text-purple-800";
    case "DELIVERED": return "bg-green-200 text-green-800";
    case "CANCELLED": return "bg-red-200 text-red-800";
    default: return "bg-gray-200 text-gray-800";
  }
}

const statusOptions = [
  "PENDING",
  "PRE_DELIVERY",
  "IN_ROUTE",
  "DELIVERED",
  "CANCELLED"
];

function renderOrders(orders) {
  ordersTableBody.innerHTML = "";
  orders.forEach(order => {
    const statusColor = getStatusColor(order.status);
    ordersTableBody.innerHTML += `
      <tr class="border-b hover:bg-[#D8E4E0]/30 transition">
        <td class="py-2 px-4 truncate max-w-[120px]">${order.id}</td>
        <td class="py-2 px-4">${order.item_id}</td>
        <td class="py-2 px-4">${order.customer_name}</td>
        <td class="py-2 px-4">${order.pickup_address}</td>
        <td class="py-2 px-4">${order.delivery_address}</td>
        <td class="py-2 px-4">${order.available_from}</td>
        <td class="py-2 px-4">${order.deadline}</td>
        <td class="py-2 px-4">
          <div class="relative inline-block w-1/2">
            <button class="w-full flex items-center justify-between px-2 py-1 rounded-full ${statusColor} focus:outline-none status-dropdown-btn">
              <span>${order.status}</span>
              <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div class="hidden absolute left-0 mt-1 w-full bg-white rounded shadow z-10 status-dropdown">
              ${statusOptions.map(opt => `
                <div class="px-3 py-1 cursor-pointer hover:bg-gray-100 rounded ${getStatusColor(opt)}" data-status="${opt}">${opt}</div>
              `).join('')}
            </div>
          </div>
        </td>
      </tr>`;
  });

  // Add dropdown logic after rendering
  document.querySelectorAll('.status-dropdown-btn').forEach((btn, idx) => {
    const wrapper = btn.parentElement;
    const dropdown = wrapper.querySelector('.status-dropdown');
    btn.onclick = (e) => {
      e.stopPropagation();
      // Toggle only this dropdown
      const isOpen = !dropdown.classList.contains('hidden');
      document.querySelectorAll('.status-dropdown').forEach(d => d.classList.add('hidden'));
      if (!isOpen) {
        dropdown.classList.remove('hidden');
      } else {
        dropdown.classList.add('hidden');
      }
    };
    dropdown.querySelectorAll('[data-status]').forEach(opt => {
      opt.onclick = async (e) => {
        e.stopPropagation();
        const newStatus = opt.getAttribute('data-status');
        const orderId = orders[idx].id;
        try {
          const response = await fetch(`${apiBase}${orderId}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_status: newStatus })
          });
          if (!response.ok) throw new Error("Failed to update status");
          fetchOrders();
        } catch (err) {
          alert("Could not update status.");
        }
        dropdown.classList.add('hidden');
      };
    });
  });
}

document.addEventListener('click', () => {
  document.querySelectorAll('.status-dropdown').forEach(d => d.classList.add('hidden'));
});

orderForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = Object.fromEntries(new FormData(orderForm).entries());

  try {
    const response = await fetch(apiBase, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });

    if (!response.ok) throw new Error("Failed to create order");
    modal.classList.add("hidden");
    orderForm.reset();
    fetchOrders();
  } catch (err) {
    console.error(err);
    alert("Could not create order.");
  }
});

newOrderBtn.onclick = () => modal.classList.remove("hidden");
closeModal.onclick = () => modal.classList.add("hidden");

modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.classList.add("hidden");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("sortAvailableFrom").onclick = () => sortOrders("available_from");
  document.getElementById("sortDeadline").onclick = () => sortOrders("deadline");
  document.getElementById("sortStatus").onclick = () => sortOrders("status");
});

fetchOrders();
