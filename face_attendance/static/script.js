const button=document.getElementById('toggle_button');
const video=document.getElementById('video_feed');
button.addEventListener('click',()=>{
    fetch('/toggle_camera').then(res=>res.json()).then(data=>{
        if(data.camera_on){button.textContent='Stop Camera';video.src='/video?'+new Date().getTime();}
        else{button.textContent='Start Camera';video.src='';}
    });
});
function updateAttendance(){
    fetch('/attendance').then(res=>res.json()).then(data=>{
        const tbody=document.querySelector('#attendance_table tbody');
        tbody.innerHTML='';
        data.forEach(student=>{
            const row=document.createElement('tr');
            row.className=student.status==='Present'?'present':'absent';
            row.innerHTML=`<td>${student.name}</td><td>${student.status}</td>`;
            tbody.appendChild(row);
        });
    });
}
setInterval(updateAttendance,3000);
updateAttendance();