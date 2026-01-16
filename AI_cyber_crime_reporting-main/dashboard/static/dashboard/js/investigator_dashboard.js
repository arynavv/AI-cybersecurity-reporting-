// Chart.js configuration
Chart.defaults.color = '#e2e8f0';
Chart.defaults.borderColor = 'rgba(148, 163, 184, 0.1)';

// Pie Chart - Cases by Type
new Chart(document.getElementById('casesByType'), {
  type: 'doughnut',
  data: {
    labels: ['Phishing', 'Ransomware', 'Data Breach', 'DDoS', 'Identity Theft'],
    datasets: [{
      data: [15, 8, 12, 6, 6],
      backgroundColor: ['#3b82f6','#ef4444','#8b5cf6','#f59e0b','#06b6d4'],
      cutout: '60%'
    }]
  },
  options: {
    responsive:true,
    maintainAspectRatio:false,
    plugins:{
      legend:{position:'bottom'},
      tooltip:{backgroundColor:'rgba(30,41,59,0.95)', titleColor:'#f1f5f9', bodyColor:'#e2e8f0'}
    }
  }
});

// Bar Chart - Performance
new Chart(document.getElementById('casesPerformance'), {
  type:'bar',
  data: { 
    labels:['Week 1','Week 2','Week 3','Week 4'], 
    datasets:[
      {label:'Resolved', data:[8,12,15,10], backgroundColor:'#22c55e', borderRadius:4, borderSkipped:false},
      {label:'New Cases', data:[12,9,11,14], backgroundColor:'#3b82f6', borderRadius:4, borderSkipped:false},
      {label:'In Progress', data:[4,6,3,8], backgroundColor:'#f59e0b', borderRadius:4, borderSkipped:false}
    ]
  },
  options:{
    responsive:true,
    maintainAspectRatio:false,
    scales:{
      x:{ticks:{color:'#94a3b8'}, grid:{color:'rgba(148,163,184,0.1)'}},
      y:{ticks:{color:'#94a3b8'}, grid:{color:'rgba(148,163,184,0.1)'}}
    },
    plugins:{legend:{labels:{color:'#e2e8f0'}}, tooltip:{backgroundColor:'rgba(30,41,59,0.95)', titleColor:'#f1f5f9', bodyColor:'#e2e8f0'}},
    interaction:{intersect:false, mode:'index'}
  }
});

// Alert interaction simulation
document.addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('.alert-item').forEach(item=>{
    item.addEventListener('click', ()=>{
      item.style.background='rgba(59,130,246,0.2)';
      setTimeout(()=>{ item.style.background=''; },300);
    });
  });

  setInterval(()=>{
    document.querySelectorAll('.alert-time').forEach(el=>{
      const time = el.textContent.split(' ')[0];
      const unit = el.textContent.split(' ')[1];
      let newTime = parseInt(time) + 1;
      el.textContent = `${newTime} ${unit} ago`;
    });
  },60000);
});
