// -----// inicio BUSQUEDA MAQUINARIA para BASICO //-----
document.getElementById('searchBoxmaterialesbasicos').addEventListener('input', function() {
    var query = this.value.toLowerCase();
    var results = document.querySelectorAll('#resultsmaterialesbasicos .resultmaterialesbasicos');
    var resultsContainer = document.getElementById('resultsmaterialesbasicos');
    var hasVisibleResults = false;

    results.forEach(function(result) {
        var text = result.textContent.toLowerCase();
        if (text.includes(query)) {
            result.classList.remove('hiddenmaterialesbasicos');
            hasVisibleResults = true;
        } else {
            result.classList.add('hiddenmaterialesbasicos');
        }
    });

    if (query.length > 0 && hasVisibleResults) {
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
});

document.getElementById('searchBoxmaterialesbasicos').addEventListener('focus', function() {
    if (this.value.length > 0) {
        document.getElementById('resultsmaterialesbasicos').style.display = 'block';
    }
});

document.getElementById('searchBoxmaterialesbasicos').addEventListener('blur', function() {
    setTimeout(function() {
        document.getElementById('resultsmaterialesbasicos').style.display = 'none';
    }, 200);
});

document.getElementById('resultsmaterialesbasicos').addEventListener('mousedown', function(e) {
    e.preventDefault();
});
// -----// fin BUSQUEDA MAQUINARIA para BASICO //-----


// -----// inicio BUSQUEDA OFICIOS para BASICO //-----
document.getElementById('searchBoxoficiosbasicos').addEventListener('input', function() {
    var query = this.value.toLowerCase();
    var results = document.querySelectorAll('#resultsoficiosbasicos .resultoficiosbasicos');
    var resultsContainer = document.getElementById('resultsoficiosbasicos');
    var hasVisibleResults = false;

    results.forEach(function(result) {
        var text = result.textContent.toLowerCase();
        if (text.includes(query)) {
            result.classList.remove('hiddenoficiosbasicos');
            hasVisibleResults = true;
        } else {
            result.classList.add('hiddenoficiosbasicos');
        }
    });

    if (query.length > 0 && hasVisibleResults) {
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
});

document.getElementById('searchBoxoficiosbasicos').addEventListener('focus', function() {
    if (this.value.length > 0) {
        document.getElementById('resultsoficiosbasicos').style.display = 'block';
    }
});

document.getElementById('searchBoxoficiosbasicos').addEventListener('blur', function() {
    setTimeout(function() {
        document.getElementById('resultsoficiosbasicos').style.display = 'none';
    }, 200);
});

document.getElementById('resultsoficiosbasicos').addEventListener('mousedown', function(e) {
    e.preventDefault();
});
// -----// fin BUSQUEDA OFICIOS para BASICO //-----