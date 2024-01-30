document.addEventListener("DOMContentLoaded", function(){

    window.addEventListener("resize", function(){
        if(this.window.innerWidth >= 1000){
            taskForm.style.display = "block";
        }else{
            taskForm.style.display = "none"; 
        }
    })

    /*FECHA ACTUAL*/
    var currentDateElement = document.getElementById("day");
    var dayOfWeekElement = document.getElementById("dayOfWeek");
    var monthYearElement = document.getElementById("monthYear");

    var currentDate = new Date();
    var optionsDay = { day: 'numeric' };
    var optionsDayOfWeek = { weekday: 'long'};
    var optionsMonthYear = { year: 'numeric', month: 'short'};

    var day = currentDate.toLocaleDateString('en-EN', optionsDay); 
    var dayOfWeek = currentDate.toLocaleDateString('en-EN', optionsDayOfWeek);
    var monthYear = currentDate.toLocaleDateString('en-EN', optionsMonthYear);

    currentDateElement.textContent = day;
    dayOfWeekElement.textContent = dayOfWeek;
    monthYearElement.textContent = monthYear;


   
    /*OPCIONES*/
    var optionButton = document.getElementById("optionsBtn");
    var menu = document.getElementById("menu-container");

    optionButton.addEventListener("click", function() {
        if(menu.style.display !== "block"){
            menu.style.display = "block";
        }else{
            menu.style.display = "none";
        }
        
    })

    /*FORMULARIO*/ 
    var addTaskButton = document.getElementById("addTaskButton");
    var taskForm = document.getElementById("taskForm");
    var add = document.getElementById("add");
    var close = document.getElementById("close");

    const nameInput = document.getElementById("name");
    const descriptionInput = document.getElementById("description");
    const dateInput = document.getElementById("dueDate");

    const pendingList = document.getElementById("pending-list");
    const allTaskList = document.getElementById("allTasks");

    const errorMsg = document.getElementById("errorMsg");

    var numberOfPendingTask = document.getElementById("task-number");
    
    addTaskButton.addEventListener("click", function() {
        taskForm.style.display = "block";
    })


    function resetForm(){
        nameInput.value = '';
        descriptionInput.value = '';
        dateInput.value = '';
        nameInput.style.borderColor = "#aaa";
        errorMsg.style.display = "none";
    }

    close.addEventListener("click", function (){
        taskForm.style.display = 'none';
    })


    add.addEventListener("click", function(event) {
        event.preventDefault();
        
        if (nameInput.value.trim() === ''){
            nameInput.style.borderColor = "red";
            errorMsg.style.display = "block";
        } else {
            const listElement = createLi();
            pendingList.appendChild(listElement);
            resetForm();
            var numberOfElements = pendingList.childElementCount;
            numberOfPendingTask.textContent = 'Active Tasks: ' + numberOfElements;
            if (window.innerWidth < 1000) {
                taskForm.style.display = "none";
            }
        } 
    })

    if(window.innerWidth >= 1000){
        taskForm.style.display = "block";
    }

    function createLi(){
        const li = document.createElement('li');
        li.textContent = nameInput.value;
        li.tabIndex = "0";
        
        
        const editButton = document.createElement('button');
        editButton.className = 'uil uil-ellipsis-h';
        li.appendChild(editButton);
        
        if(dateInput.value !== ""){
            const date = document.createElement('p');
            date.textContent = formatDateFromISO(dateInput.value);
            li.appendChild(date);
        }
        if(descriptionInput.value !== ""){
            const description = document.createElement('p');
            description.textContent = descriptionInput.value;
            li.appendChild(description);
        }

        const container = document.createElement('div');
        container.className = 'edit-container';
        //container.id = 
        const editTask = document.createElement('button');
        editTask.textContent = "Edit";
        editTask.className = "containerButton";
        const deleteTask = document.createElement('button');
        deleteTask.textContent = "Delete";
        deleteTask.className = "containerButton";

        container.appendChild(editTask);
        container.appendChild(deleteTask);
        
        li.appendChild(container);
        return li;
        
    }

    /*EDIT TASK*/
    
    allTaskList.addEventListener('click', (event) => {
        if( event.target.className === 'uil uil-ellipsis-h') {
            const button = event.target;
            const li = button.parentNode;
            const container = li.lastChild;
            const ul = li.parentNode;
            
            if(container.style.display !== "block"){
                container.style.display = "block";

                container.addEventListener('click', (event) =>{
                    if(event.target.textContent === 'Delete'){
                        
                        ul.removeChild(li);
                        var numberOfElements = pendingList.childElementCount;
                        numberOfPendingTask.textContent = 'Active Tasks: ' + numberOfElements;

                    }
                });

    
            }else{
                container.style.display = "none";
            }
        } 
    });

    function formatDateFromISO(dateISO) {

        var date = new Date(dateISO);
        var day = date.getDate();
        var months = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"    ];
        var monthName = months[date.getMonth()];
        var year = date.getFullYear();
        var formattedDate = day + ' ' + monthName + ' ' + year;
    
        return formattedDate;
    }
    

});