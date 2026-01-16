// Sample dynamic data for User Dashboard

// Stats
document.getElementById('tasks-completed').innerText = 24;
document.getElementById('alerts-count').innerText = 5;
document.getElementById('projects-count').innerText = 3;

// Alerts
const alerts = [
    { type: 'info', text: 'New message from Admin', time: '2m ago' },
    { type: 'warning', text: 'Task overdue', time: '1h ago' },
    { type: 'info', text: 'System maintenance scheduled', time: '3h ago' }
];

const alertsList = document.getElementById('alerts-list');

alerts.forEach(alert => {
    const li = document.createElement('li');
    li.className = `alert-item ${alert.type}`;
    li.innerHTML = `<div class="alert-text">${alert.text}</div><div class="alert-time">${alert.time}</div>`;
    alertsList.appendChild(li);
});

// Tasks Table
const tasks = [
    { task: 'Finish report', status: 'In Progress', priority: 'High' },
    { task: 'Team meeting', status: 'Open', priority: 'Medium' },
    { task: 'Update documentation', status: 'Resolved', priority: 'Low' }
];

const tasksTable = document.getElementById('tasks-table');

tasks.forEach(t => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${t.task}</td>
        <td><span class="status status-${t.status.toLowerCase().replace(' ', '-')}">${t.status}</span></td>
        <td><span class="priority priority-${t.priority.toLowerCase()}">${t.priority}</span></td>
    `;
    tasksTable.appendChild(tr);
});
