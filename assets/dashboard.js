(() => {
  const driversRaw = sessionStorage.getItem('drivers');
  const ridersRaw = sessionStorage.getItem('riders');

  function showError(msg){
    document.querySelector('.dashboard').innerHTML = `
      <div class="glass card" style="text-align:center;padding:40px">
        <h2 class="neon-sub">⚠️ ${msg}</h2>
        <p class="muted">Please upload datasets first to view the dashboard.</p>
        <div style="margin-top:20px">
          <a href="upload.html" class="btn btn-primary glow">📤 Upload Datasets</a>
          <a href="index.html" class="btn btn-ghost">🏠 Back to Home</a>
        </div>
      </div>
    `;
  }

  if(!driversRaw || !ridersRaw){
    showError('No datasets found');
    return;
  }

  let drivers, riders;
  try{
    drivers = JSON.parse(driversRaw);
    riders = JSON.parse(ridersRaw);
  }catch(err){
    showError('Error parsing datasets');
    return;
  }

  // Utility: Haversine distance in km
  function haversine([lat1, lon1], [lat2, lon2]){
    const toRad = v => v * Math.PI / 180;
    const R = 6371; // Earth radius in km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat/2)**2 + Math.cos(toRad(lat1))*Math.cos(toRad(lat2)) * Math.sin(dLon/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  // Update metric cards
  document.getElementById('driverCount').textContent = drivers.length;
  document.getElementById('riderCount').textContent = riders.length;
  
  const avgRating = drivers.reduce((sum, d) => sum + (d.rating || 0), 0) / drivers.length;
  document.getElementById('avgRating').textContent = avgRating.toFixed(1);

  // Chart: Driver vs Rider
  const ctxBar = document.getElementById('barChart').getContext('2d');
  new Chart(ctxBar, {
    type: 'bar',
    data: {
      labels: ['Drivers','Riders'],
      datasets: [{
        label:'Count',
        data:[drivers.length, riders.length],
        backgroundColor:['rgba(0,229,255,0.6)','rgba(255,0,230,0.6)'],
        borderColor:['#00E5FF','#FF00E6'],
        borderWidth: 2
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins:{
        legend:{display:false}
      },
      scales:{
        y:{
          beginAtZero:true,
          grid:{color:'rgba(255,255,255,0.05)'},
          ticks:{color:'rgba(255,255,255,0.7)'}
        },
        x:{
          grid:{display:false},
          ticks:{color:'rgba(255,255,255,0.7)'}
        }
      }
    }
  });

  // Vehicle distribution
  const vehicleCounts = {};
  drivers.forEach(d => {
    const vType = d.vehicle_type || 'Unknown';
    vehicleCounts[vType] = (vehicleCounts[vType]||0)+1;
  });
  
  const pieLabels = Object.keys(vehicleCounts);
  const pieData = Object.values(vehicleCounts);
  const colors = ['#00E5FF','#FF00E6','#F9A825','#7B2FF7','#42A5F5','#5E35B1'];
  
  const ctxPie = document.getElementById('pieChart').getContext('2d');
  new Chart(ctxPie, {
    type:'pie',
    data:{
      labels:pieLabels,
      datasets:[{
        data:pieData,
        backgroundColor:colors.slice(0, pieLabels.length),
        borderColor:'rgba(0,0,0,0.5)',
        borderWidth:2
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio: true,
      aspectRatio: 1,
      plugins:{
        legend:{
          position:'bottom',
          labels:{color:'rgba(255,255,255,0.8)',padding:10}
        }
      }
    }
  });

  // Matching logic
  function trafficWeight(zone){
    if(!zone) return 0.9;
    zone = zone.toLowerCase();
    if(zone.includes('low')) return 1.0;
    if(zone.includes('medium')) return 0.9;
    if(zone.includes('high')) return 0.75;
    return 0.9;
  }
  
  function urgencyWeight(urg){
    if(!urg) return 1.0;
    urg = urg.toLowerCase();
    if(urg.includes('high')) return 1.3;
    if(urg.includes('medium')) return 1.0;
    if(urg.includes('low')) return 0.8;
    return 1.0;
  }

  function scoreDriverForRider(driver, rider){
    const status = (driver.status || 'available').toLowerCase();
    if(status !== 'available') return {score: -9999, distance: -1};
    
    const dist = haversine(driver.location, rider.location);
    const maxDist = 50; // km window
    const distNorm = Math.min(dist, maxDist);
    
    // Distance score: closer = higher (0-50 points)
    const distanceScore = Math.max(0, 50 - (distNorm / maxDist) * 50);
    
    // Vehicle preference match (0-30 points)
    const vehicleBonus = (driver.vehicle_type && rider.preferred_vehicle && 
                         driver.vehicle_type.toLowerCase() === rider.preferred_vehicle.toLowerCase()) ? 30 : 0;
    
    // Rating bonus (0-20 points based on actual rating)
    const ratingBonus = (driver.rating ? (driver.rating/5) * 20 : 0);
    
    // Apply traffic and urgency weights
    const tW = trafficWeight(driver.traffic_zone);
    const uW = urgencyWeight(rider.urgency);
    
    const raw = (distanceScore + vehicleBonus + ratingBonus) * tW * uW;
    return {score: Math.round(raw*100)/100, distance: Math.round(dist*100)/100};
  }

  const matchesList = document.getElementById('matchesList');
  matchesList.innerHTML = '';
  
  const allMatches = [];

  riders.forEach(rider => {
    const scored = drivers.map(d => ({
      driver:d, 
      rider:rider,
      ...scoreDriverForRider(d, rider)
    })).filter(x => x.score > -9000);
    
    scored.sort((a,b) => b.score - a.score);
    const top = scored.slice(0, 3);
    
    if(top.length > 0){
      allMatches.push({rider, matches: top});
    }

    const item = document.createElement('div');
    item.className = 'match';
    
    const left = document.createElement('div');
    left.className='left';
    left.innerHTML = `
      <strong>👤 Rider #${rider.rider_id}</strong>
      <small class="muted">
        📍 Location: [${rider.location[0].toFixed(4)}, ${rider.location[1].toFixed(4)}]<br>
        🚙 Prefers: ${rider.preferred_vehicle || 'Any'} • 
        ⏱️ Urgency: ${rider.urgency || 'Normal'}
      </small>
    `;

    const right = document.createElement('div');
    right.className='right';
    
    if(top.length === 0){
      right.innerHTML = '<span class="pill">❌ No available drivers</span>';
    } else {
      top.forEach((t, idx) => {
        const rank = ['🥇','🥈','🥉'][idx] || '🔹';
        const matchDiv = document.createElement('div');
        matchDiv.style.marginBottom = '8px';
        matchDiv.innerHTML = `
          <span class="pill">
            ${rank} Driver #${t.driver.driver_id} • ${t.driver.vehicle_type} • 
            ${t.distance} km • ⭐ ${t.driver.rating || 'N/A'} • 
            <strong style="color:#00e5ff">Score: ${t.score}</strong>
          </span>
        `;
        right.appendChild(matchDiv);
      });
    }

    item.appendChild(left);
    item.appendChild(right);
    matchesList.appendChild(item);
  });

  // Update match count
  document.getElementById('matchCount').textContent = allMatches.reduce((sum, m) => sum + m.matches.length, 0);

  // ========== NEW ANALYTICS CHARTS ==========

  // 3️⃣ Match Efficiency Chart
  const efficiencyCounts = {first: 0, second: 0, third: 0, none: 0};
  allMatches.forEach(m => {
    if(m.matches.length >= 1) efficiencyCounts.first++;
    if(m.matches.length >= 2) efficiencyCounts.second++;
    if(m.matches.length >= 3) efficiencyCounts.third++;
    if(m.matches.length === 0) efficiencyCounts.none++;
  });

  const ctxEfficiency = document.getElementById('efficiencyChart').getContext('2d');
  new Chart(ctxEfficiency, {
    type: 'bar',
    data: {
      labels: ['1st Choice', '2nd Choice', '3rd Choice'],
      datasets: [{
        label: 'Riders',
        data: [efficiencyCounts.first, efficiencyCounts.second, efficiencyCounts.third],
        backgroundColor: ['rgba(0,229,255,0.7)', 'rgba(255,0,230,0.7)', 'rgba(249,168,37,0.7)'],
        borderColor: ['#00E5FF', '#FF00E6', '#F9A825'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: {color: 'rgba(255,255,255,0.05)'}, ticks: {color: 'rgba(255,255,255,0.7)'} },
        x: { grid: {display: false}, ticks: {color: 'rgba(255,255,255,0.7)'} }
      }
    }
  });

  // 4️⃣ Average Ride Distance by Vehicle Type
  const distanceByVehicle = {};
  allMatches.forEach(m => {
    m.matches.forEach(match => {
      const vType = match.driver.vehicle_type || 'Unknown';
      if(!distanceByVehicle[vType]) distanceByVehicle[vType] = {total: 0, count: 0};
      distanceByVehicle[vType].total += match.distance;
      distanceByVehicle[vType].count++;
    });
  });

  const avgDistLabels = Object.keys(distanceByVehicle);
  const avgDistData = avgDistLabels.map(v => (distanceByVehicle[v].total / distanceByVehicle[v].count).toFixed(2));

  const ctxDistance = document.getElementById('distanceChart').getContext('2d');
  new Chart(ctxDistance, {
    type: 'bar',
    data: {
      labels: avgDistLabels,
      datasets: [{
        label: 'Avg Distance (km)',
        data: avgDistData,
        backgroundColor: 'rgba(123,47,247,0.7)',
        borderColor: '#7B2FF7',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: {color: 'rgba(255,255,255,0.05)'}, ticks: {color: 'rgba(255,255,255,0.7)'} },
        x: { grid: {display: false}, ticks: {color: 'rgba(255,255,255,0.7)'} }
      }
    }
  });

  // 5️⃣ Urgency Distribution
  const urgencyCounts = {high: 0, medium: 0, low: 0};
  riders.forEach(r => {
    const urg = (r.urgency || 'medium').toLowerCase();
    if(urg.includes('high')) urgencyCounts.high++;
    else if(urg.includes('low')) urgencyCounts.low++;
    else urgencyCounts.medium++;
  });

  const ctxUrgency = document.getElementById('urgencyChart').getContext('2d');
  new Chart(ctxUrgency, {
    type: 'pie',
    data: {
      labels: ['High', 'Medium', 'Low'],
      datasets: [{
        data: [urgencyCounts.high, urgencyCounts.medium, urgencyCounts.low],
        backgroundColor: ['rgba(255,0,230,0.7)', 'rgba(249,168,37,0.7)', 'rgba(0,229,255,0.7)'],
        borderColor: 'rgba(0,0,0,0.5)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1.5,
      plugins: {
        legend: { position: 'bottom', labels: {color: 'rgba(255,255,255,0.8)', padding: 8, font: {size: 11}} }
      }
    }
  });

  // 6️⃣ Driver Ratings Distribution
  const ratingBuckets = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0};
  drivers.forEach(d => {
    const rating = Math.floor(d.rating || 0);
    if(rating >= 1 && rating <= 5) ratingBuckets[rating]++;
  });

  const ctxRatings = document.getElementById('ratingsChart').getContext('2d');
  new Chart(ctxRatings, {
    type: 'bar',
    data: {
      labels: ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'],
      datasets: [{
        label: 'Drivers',
        data: [ratingBuckets[1], ratingBuckets[2], ratingBuckets[3], ratingBuckets[4], ratingBuckets[5]],
        backgroundColor: 'rgba(249,168,37,0.7)',
        borderColor: '#F9A825',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: {color: 'rgba(255,255,255,0.05)'}, ticks: {color: 'rgba(255,255,255,0.7)'} },
        x: { grid: {display: false}, ticks: {color: 'rgba(255,255,255,0.7)'} }
      }
    }
  });

  // 7️⃣ Match Score Distribution
  const allScores = [];
  allMatches.forEach(m => m.matches.forEach(match => allScores.push(match.score)));
  
  const scoreBuckets = [0, 0, 0, 0, 0]; // 0-20, 20-40, 40-60, 60-80, 80-100
  allScores.forEach(score => {
    const bucket = Math.min(Math.floor(score / 20), 4);
    scoreBuckets[bucket]++;
  });

  const ctxScore = document.getElementById('scoreChart').getContext('2d');
  new Chart(ctxScore, {
    type: 'bar',
    data: {
      labels: ['0-20', '20-40', '40-60', '60-80', '80-100'],
      datasets: [{
        label: 'Matches',
        data: scoreBuckets,
        backgroundColor: 'rgba(0,229,255,0.7)',
        borderColor: '#00E5FF',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: {color: 'rgba(255,255,255,0.05)'}, ticks: {color: 'rgba(255,255,255,0.7)'} },
        x: { grid: {display: false}, ticks: {color: 'rgba(255,255,255,0.7)'} }
      }
    }
  });

  // 9️⃣ Rider Vehicle Preferences
  const prefCounts = {};
  riders.forEach(r => {
    const pref = r.preferred_vehicle || 'Any';
    prefCounts[pref] = (prefCounts[pref] || 0) + 1;
  });

  const prefLabels = Object.keys(prefCounts);
  const prefData = Object.values(prefCounts);

  const ctxPreferences = document.getElementById('preferencesChart').getContext('2d');
  new Chart(ctxPreferences, {
    type: 'pie',
    data: {
      labels: prefLabels,
      datasets: [{
        data: prefData,
        backgroundColor: ['#00E5FF', '#FF00E6', '#F9A825', '#7B2FF7', '#42A5F5', '#5E35B1'],
        borderColor: 'rgba(0,0,0,0.5)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1.5,
      plugins: {
        legend: { position: 'bottom', labels: {color: 'rgba(255,255,255,0.8)', padding: 8, font: {size: 11}} }
      }
    }
  });

  // 8️⃣ Top Performing Drivers Table
  const driverStats = {};
  drivers.forEach(d => {
    driverStats[d.driver_id] = {
      driver: d,
      matchCount: 0,
      totalDistance: 0,
      distances: []
    };
  });

  allMatches.forEach(m => {
    m.matches.forEach(match => {
      const dId = match.driver.driver_id;
      if(driverStats[dId]) {
        driverStats[dId].matchCount++;
        driverStats[dId].totalDistance += match.distance;
        driverStats[dId].distances.push(match.distance);
      }
    });
  });

  const topDrivers = Object.values(driverStats)
    .filter(d => d.matchCount > 0)
    .sort((a, b) => {
      // Sort by: 1) match count desc, 2) rating desc, 3) avg distance asc
      if(b.matchCount !== a.matchCount) return b.matchCount - a.matchCount;
      if((b.driver.rating || 0) !== (a.driver.rating || 0)) return (b.driver.rating || 0) - (a.driver.rating || 0);
      return (a.totalDistance / a.matchCount) - (b.totalDistance / b.matchCount);
    })
    .slice(0, 10);

  const tableBody = document.querySelector('#topDriversTable tbody');
  topDrivers.forEach((d, idx) => {
    const avgDist = (d.totalDistance / d.matchCount).toFixed(2);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${idx + 1}</td>
      <td>#${d.driver.driver_id}</td>
      <td>${d.driver.name || 'N/A'}</td>
      <td>⭐ ${d.driver.rating || 'N/A'}</td>
      <td>${d.matchCount}</td>
      <td>${avgDist}</td>
      <td>${d.driver.vehicle_type || 'N/A'}</td>
    `;
    tableBody.appendChild(row);
  });

  // 10️⃣ Zone-Based Analytics
  const zoneData = {};
  allMatches.forEach(m => {
    m.matches.forEach(match => {
      const zone = match.driver.traffic_zone || 'Unknown';
      if(!zoneData[zone]) zoneData[zone] = {matches: 0, totalScore: 0, totalDistance: 0};
      zoneData[zone].matches++;
      zoneData[zone].totalScore += match.score;
      zoneData[zone].totalDistance += match.distance;
    });
  });

  const zoneStats = document.getElementById('zoneStats');
  Object.keys(zoneData).sort().forEach(zone => {
    const data = zoneData[zone];
    const avgScore = (data.totalScore / data.matches).toFixed(2);
    const avgDist = (data.totalDistance / data.matches).toFixed(2);
    
    const zoneCard = document.createElement('div');
    zoneCard.className = 'zone-card';
    zoneCard.innerHTML = `
      <div class="zone-header">
        <h4>📍 ${zone}</h4>
        <span class="pill">${data.matches} matches</span>
      </div>
      <div class="zone-metrics">
        <div class="zone-metric">
          <span class="zone-metric-label">Avg Score</span>
          <span class="zone-metric-value">${avgScore}</span>
        </div>
        <div class="zone-metric">
          <span class="zone-metric-label">Avg Distance</span>
          <span class="zone-metric-value">${avgDist} km</span>
        </div>
      </div>
    `;
    zoneStats.appendChild(zoneCard);
  });

  // Export functionality - Excel/CSV format
  document.getElementById('exportBtn').addEventListener('click', () => {
    // Create CSV content
    let csvContent = 'Rider ID,Rider Location,Preferred Vehicle,Urgency,Rank,Driver ID,Driver Name,Vehicle Type,Rating,Distance (km),Match Score,Traffic Zone\n';
    
    allMatches.forEach(m => {
      m.matches.forEach((match, idx) => {
        const rank = idx + 1;
        csvContent += `${m.rider.rider_id},"[${m.rider.location[0]}, ${m.rider.location[1]}]",${m.rider.preferred_vehicle || 'Any'},${m.rider.urgency || 'Normal'},${rank},${match.driver.driver_id},${match.driver.name || 'N/A'},${match.driver.vehicle_type},${match.driver.rating},${match.distance},${match.score},${match.driver.traffic_zone}\n`;
      });
    });
    
    // Create downloadable file
    const blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ride-matching-results-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  });

})();
