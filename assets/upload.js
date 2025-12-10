(() => {
  const driversFile = document.getElementById('driversFile');
  const ridersFile = document.getElementById('ridersFile');
  const uploadBtn = document.getElementById('uploadBtn');
  const message = document.getElementById('message');
  const driversBox = document.getElementById('driversBox');
  const ridersBox = document.getElementById('ridersBox');
  const driversFileName = document.getElementById('driversFileName');
  const ridersFileName = document.getElementById('ridersFileName');
  const btnText = document.getElementById('btnText');
  const btnLoader = document.getElementById('btnLoader');

  function setMsg(txt, type = ''){
    message.textContent = txt;
    message.className = 'message ' + type;
  }

  function checkReady(){
    const ready = driversFile.files.length && ridersFile.files.length;
    uploadBtn.disabled = !ready;
    
    if(driversFile.files.length){
      driversFileName.textContent = driversFile.files[0].name;
      driversBox.classList.add('has-file');
    }
    
    if(ridersFile.files.length){
      ridersFileName.textContent = ridersFile.files[0].name;
      ridersBox.classList.add('has-file');
    }
  }

  driversFile.addEventListener('change', checkReady);
  ridersFile.addEventListener('change', checkReady);

  function validateDriverData(drivers){
    if(!Array.isArray(drivers)) throw new Error('Drivers data must be an array');
    if(drivers.length === 0) throw new Error('Drivers array is empty');
    
    drivers.forEach((d, i) => {
      if(!d.driver_id) throw new Error(`Driver at index ${i} missing driver_id`);
      if(!Array.isArray(d.location) || d.location.length !== 2){
        throw new Error(`Driver ${d.driver_id} has invalid location (must be [lat, lon])`);
      }
      if(typeof d.location[0] !== 'number' || typeof d.location[1] !== 'number'){
        throw new Error(`Driver ${d.driver_id} location coordinates must be numbers`);
      }
      if(!d.vehicle_type) throw new Error(`Driver ${d.driver_id} missing vehicle_type`);
    });
    
    return true;
  }

  function validateRiderData(riders){
    if(!Array.isArray(riders)) throw new Error('Riders data must be an array');
    if(riders.length === 0) throw new Error('Riders array is empty');
    
    riders.forEach((r, i) => {
      if(!r.rider_id) throw new Error(`Rider at index ${i} missing rider_id`);
      if(!Array.isArray(r.location) || r.location.length !== 2){
        throw new Error(`Rider ${r.rider_id} has invalid location (must be [lat, lon])`);
      }
      if(typeof r.location[0] !== 'number' || typeof r.location[1] !== 'number'){
        throw new Error(`Rider ${r.rider_id} location coordinates must be numbers`);
      }
    });
    
    return true;
  }

  function readJSONFile(file){
    return new Promise((res, rej) => {
      const reader = new FileReader();
      reader.onload = e => {
        try{
          const parsed = JSON.parse(e.target.result);
          res(parsed);
        }catch(err){ 
          rej(new Error(`Invalid JSON in ${file.name}: ${err.message}`));
        }
      };
      reader.onerror = () => rej(new Error(`Could not read file: ${file.name}`));
      reader.readAsText(file);
    });
  }

  uploadBtn.addEventListener('click', async ()=>{
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    uploadBtn.disabled = true;
    setMsg('Processing files...', 'success');
    
    try{
      const drivers = await readJSONFile(driversFile.files[0]);
      validateDriverData(drivers);
      
      const riders = await readJSONFile(ridersFile.files[0]);
      validateRiderData(riders);

      sessionStorage.setItem('drivers', JSON.stringify(drivers));
      sessionStorage.setItem('riders', JSON.stringify(riders));

      setMsg(`✓ Successfully processed ${drivers.length} drivers and ${riders.length} riders. Redirecting...`, 'success');
      setTimeout(()=> window.location.href = 'dashboard.html', 1000);
    }catch(err){
      setMsg('✗ ' + err.message, 'error');
      btnText.style.display = 'inline';
      btnLoader.style.display = 'none';
      uploadBtn.disabled = false;
    }
  });
})();
