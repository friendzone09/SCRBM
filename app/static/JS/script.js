document.addEventListener('DOMContentLoaded', (event) => {

    document.getElementById('input_titulo_proyecto').addEventListener('input', function(){
        document.getElementById('tiutlo_proyecto').innerText = this.value;
    });
    
    
    // ABRIR CERRA MODAL CREAR PROYECTO POR JS
    
    const modal_crear_proyecto = document.getElementById('id_modal_crear_proyecto');
    
    const btn_abrir_modal_crear_proyecto = document.getElementById('abrir_modal_crear_proyecto');
    
    const btn_cancelar_proyecto = document.getElementById('btn_cancelar_proyecto');
    
    btn_abrir_modal_crear_proyecto.addEventListener('click', () =>{

        modal_crear_proyecto.classList.add('mostrar_modal_crear_proyecto');
        
    })


    btn_cancelar_proyecto.addEventListener('click', () =>{

        modal_crear_proyecto.classList.remove('mostrar_modal_crear_proyecto');
    })
    
    
    
    // FIN ABRIR CERRA MODAL CREAR PROYECTO POR JS




    //ABRIR CERRAR MODAL ELIMINAR UNIDAD POR JS
    

    //FIN ABRIR CERRAR MODAL ELIMINAR UNIDAD POR JS 
});




//CALCULAR TOTAL MATERIALES
//RECUERDA< BORRALO, pero ya tienes una idea uwu


    const formContainer = document.getElementById("form-container");
    const addFieldButton = document.getElementById("add-field");
    const totalElement = document.getElementById("total");
    const materialOptionsTemplate = document.getElementById("material-options").innerHTML;

    let fieldCount = 1;

    function calculateTotal() {
        let total = 0;
        const selects = document.querySelectorAll(".material-select");
        selects.forEach(select => {
            const cost = parseFloat(select.value) || 0;
            total += cost;
        });
        totalElement.textContent = total.toFixed(2);
    }

    formContainer.addEventListener("change", function (event) {
        if (event.target.classList.contains("material-select")) {
            calculateTotal();
        }
    });

    addFieldButton.addEventListener("click", function () {
        fieldCount++;
        const newFieldGroup = document.createElement("div");
        newFieldGroup.className = "form-group";
        newFieldGroup.innerHTML = `
            <label for="material${fieldCount}">Material ${fieldCount}:</label>
            <select name="material${fieldCount}" id="material${fieldCount}" class="material-select">
                ${materialOptionsTemplate}
            </select>
        `;
        formContainer.appendChild(newFieldGroup);
    });







