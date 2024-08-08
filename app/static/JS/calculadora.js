//MATERIALES BASICOS
const opciones_materiales = document.getElementById('opciones_mat').innerHTML
let btn_agr_mat_basico = document.getElementById('btn_agregar_materiales_basico');
let cont_padre_mat_basico = document.querySelector('.form2_basico');
let totalMatBasInput = document.getElementById('total_mat_bas');
let resulMatBas = [];
let contMateriales = 0;



function agregarEventoMulMatBas(selectMatBas, inputCantBas, inputImporBas, index){
    function calcuResMatBas(){
        let selectedOption = selectMatBas.options[selectMatBas.selectedIndex];
        let precioMat = parseFloat(selectedOption.getAttribute('data-price')) || 0;
        let cantMatBas = parseFloat(inputCantBas.value) || 0;
        resulMatBas[index] = precioMat * cantMatBas;
        inputImporBas.value = resulMatBas[index];
        totalMatBas();
        sumTodoBas();
    }

    selectMatBas.addEventListener('change', calcuResMatBas);
    inputCantBas.addEventListener('input', calcuResMatBas);

    function totalMatBas(){
        let sumTotal1 = resulMatBas.reduce((acc, curr) => acc + curr, 0);
        totalMatBasInput.value= sumTotal1;
        sumTodoBas();
    }

}


btn_agr_mat_basico.addEventListener('click', () => {
    contMateriales = contMateriales + 1;
    let nuevosInputsMat = document.createElement('div');
    nuevosInputsMat.classList.add('form_mat_basico');
    nuevosInputsMat.innerHTML = `<select name="" id="" class="material_select_bas">
                        ${opciones_materiales}
                    </select>
                    <input type="number" placeholder="Ingresa una cantidad" class="cant_mat_bas" id="cant_mat_bas[${contMateriales}]">
                    <input type="number" readonly placeholder="Importe" class="imp_mat_bas" id="imp_mat_bas[${contMateriales}]">`;

    cont_padre_mat_basico.append(nuevosInputsMat);

    console.log(nuevosInputsMat);

    let selectMatBas = nuevosInputsMat.querySelector('.material_select_bas');
    let inputCantBas = nuevosInputsMat.querySelector('.cant_mat_bas');
    let inputImporBas = nuevosInputsMat.querySelector('.imp_mat_bas');

    let index = resulMatBas.length;
    resulMatBas.push(0);

    agregarEventoMulMatBas(selectMatBas, inputCantBas, inputImporBas, index);

});

let selectMatBas = document.querySelector('.form_mat_basico .material_select_bas');
let inputCantBas = document.querySelector('.form_mat_basico .cant_mat_bas');
let inputImporBas = document.querySelector('.form_mat_basico .imp_mat_bas');
agregarEventoMulMatBas(selectMatBas, inputCantBas, inputImporBas, 0);

//OFICIOS BASICOS

const opciones_oficio = document.getElementById('opciones_oficios').innerHTML;
let btn_agregar_oficio_basico = document.getElementById('btn_agregar_oficios_basico');
let cont_padre_oficios_basico = document.querySelector('.form3_basico');
let total_oficios_basico = document.getElementById('imp_oficio_basico');
let precioTotalOfic = document.getElementById('total_oficios_basico');
let inputRendOficiosBasico = document.getElementById('rend_ofi_basico');
let resulOficiosBasico = [];



function agregarEventoMulOficioBas(selectOficioBasico,inputCantOficio, index2){
    function calcuResOficiosBas(){
        let selectedOptionMat = selectOficioBasico.options[selectOficioBasico.selectedIndex];
        let precioOficio = parseFloat(selectedOptionMat.getAttribute('data-price')) || 0;
        let cantOficio = parseFloat(inputCantOficio.value) || 0;
        resulOficiosBasico[index2] = precioOficio * cantOficio;
        totalOficiosBasicos();
        sumTodoBas();
    };

    selectOficioBasico.addEventListener('change', calcuResOficiosBas);
    inputCantOficio.addEventListener('input', calcuResOficiosBas);

    selectOficioBasico.addEventListener('change', CalculateRend);
    inputCantOficio.addEventListener('input', CalculateRend);

    selectOficioBasico.addEventListener('change', precio_total_herr_bas);
    inputCantOficio.addEventListener('input', precio_total_herr_bas);
    

    function totalOficiosBasicos(){
        let sumTotal2 = resulOficiosBasico.reduce((acc, curr) => acc + curr, 0);
        total_oficios_basico.value= sumTotal2;
        sumTodoBas();
    };

    inputRendOficiosBasico.addEventListener('input', CalculateRend);
    inputRendOficiosBasico.addEventListener('input', precio_total_herr_bas);

    function CalculateRend(){
        let divRend = parseFloat(inputRendOficiosBasico.value / 390);
        let mulRendCosto = divRend * total_oficios_basico.value;
        precioTotalOfic.value= mulRendCosto;
        sumTodoBas();
        console.log(divRend);
        console.log(mulRendCosto);
    }

};


btn_agregar_oficio_basico.addEventListener('click', () => {
    let nuevosInputsOficios = document.createElement('div');
    nuevosInputsOficios.classList.add('form_oficio_basico');
    nuevosInputsOficios.innerHTML = `<select name="" id="" class="oficio_select_basico">
                        ${opciones_oficio}
                    </select>
                    <input type="number" placeholder="Ingresa una Cantidad" class="cant_oficio_basico">`;

    cont_padre_oficios_basico.append(nuevosInputsOficios);

    let selectOficioBasico = nuevosInputsOficios.querySelector('.oficio_select_basico');
    let inputCantOficio = nuevosInputsOficios.querySelector('.cant_oficio_basico');

    let index2 = resulOficiosBasico.length;
    resulOficiosBasico.push(0);

    agregarEventoMulOficioBas(selectOficioBasico, inputCantOficio, index2)
    

});

let selectOficioBasico = document.querySelector('.form_oficio_basico .oficio_select_basico');
let inputCantOficio = document.querySelector('.form_oficio_basico .cant_oficio_basico');
agregarEventoMulOficioBas(selectOficioBasico, inputCantOficio, 0)

//Herramientas basico

let precio_herr_bas = document.getElementById('precio_herr_bas');
let por_herr_bas = document.getElementById('por_herr_bas');
let total_herr_bas = document.getElementById('imp_herr_bas')

function precio_total_herr_bas () {
    let precio = precioTotalOfic.value;
    precio_herr_bas.value = precio
    let porcentaje = parseFloat(por_herr_bas.value)/ 100 || 0;

    total_herr_bas.value = precio * porcentaje;
    sumTodoBas();
}

 precio_herr_bas.addEventListener('input', precio_total_herr_bas);
 por_herr_bas.addEventListener('input', precio_total_herr_bas);


 //Calcular total BASICOOOO

 let SumaFinalBas = document.getElementById('total_bas');
  function sumTodoBas(){
    let sumTotal1 = resulMatBas.reduce((acc, curr) => acc + curr, 0);
    let sumTotal2 = parseFloat(precioTotalOfic.value) || 0;
    let totalHerrValue = parseFloat(total_herr_bas.value) || 0;
    
    let sumFinalBas = sumTotal1 + sumTotal2 + totalHerrValue;
    SumaFinalBas.value = sumFinalBas;
  }