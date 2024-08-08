

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
    
    
    














