//
// !!!!!! ADVERTENCIA: TODO ESTO ES PARA CONCEPTOS !!!!!!!!
//

// -----// inicio BUSQUEDA MATERIALES //-----
document.getElementById('searchBoxmats').addEventListener('input', function() {
    var query = this.value.toLowerCase();
    var results = document.querySelectorAll('#resultsmats .resultmats');
    var resultsContainer = document.getElementById('resultsmats');
    var hasVisibleResults = false;

    results.forEach(function(result) {
        var text = result.textContent.toLowerCase();
        if (text.includes(query)) {
            result.classList.remove('hiddenmats');
            hasVisibleResults = true;
        } else {
            result.classList.add('hiddenmats');
        }
    });

    if (query.length > 0 && hasVisibleResults) {
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
});

document.getElementById('searchBoxmats').addEventListener('focus', function() {
    if (this.value.length > 0) {
        document.getElementById('resultsmats').style.display = 'block';
    }
});

document.getElementById('searchBoxmats').addEventListener('blur', function() {
    setTimeout(function() {
        document.getElementById('resultsmats').style.display = 'none';
    }, 200);
});

document.getElementById('resultsmats').addEventListener('mousedown', function(e) {
    e.preventDefault();
});
// -----// fin BUSQUEDA MATERIALES //-----



// -----// inicio BUSQUEDA MAQUINARIA //-----
document.getElementById('searchBoxmaqs').addEventListener('input', function() {
    var query = this.value.toLowerCase();
    var results = document.querySelectorAll('#resultsmaqs .resultmaqs');
    var resultsContainer = document.getElementById('resultsmaqs');
    var hasVisibleResults = false;

    results.forEach(function(result) {
        var text = result.textContent.toLowerCase();
        if (text.includes(query)) {
            result.classList.remove('hiddenmaqs');
            hasVisibleResults = true;
        } else {
            result.classList.add('hiddenmaqs');
        }
    });

    if (query.length > 0 && hasVisibleResults) {
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
});

document.getElementById('searchBoxmaqs').addEventListener('focus', function() {
    if (this.value.length > 0) {
        document.getElementById('resultsmaqs').style.display = 'block';
    }
});

document.getElementById('searchBoxmaqs').addEventListener('blur', function() {
    setTimeout(function() {
        document.getElementById('resultsmaqs').style.display = 'none';
    }, 200);
});

document.getElementById('resultsmaqs').addEventListener('mousedown', function(e) {
    e.preventDefault();
});
// -----// fin BUSQUEDA MAQUINARIA //-----



// -----// inicio BUSQUEDA BASICOS //-----
document.getElementById('searchBoxbasi').addEventListener('input', function() {
    var query = this.value.toLowerCase();
    var results = document.querySelectorAll('#resultsbasi .resultbasi');
    var resultsContainer = document.getElementById('resultsbasi');
    var hasVisibleResults = false;

    results.forEach(function(result) {
        var text = result.textContent.toLowerCase();
        if (text.includes(query)) {
            result.classList.remove('hiddenbasi');
            hasVisibleResults = true;
        } else {
            result.classList.add('hiddenbasi');
        }
    });

    if (query.length > 0 && hasVisibleResults) {
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
});

document.getElementById('searchBoxbasi').addEventListener('focus', function() {
    if (this.value.length > 0) {
        document.getElementById('resultsbasi').style.display = 'block';
    }
});

document.getElementById('searchBoxbasi').addEventListener('blur', function() {
    setTimeout(function() {
        document.getElementById('resultsbasi').style.display = 'none';
    }, 200);
});

document.getElementById('resultsbasi').addEventListener('mousedown', function(e) {
    e.preventDefault();
});
// -----// fin BUSQUEDA BASICOS //-----

// -----// inicio BUSQUEDA OFICIOS //-----
document.getElementById('searchBoxoficon').addEventListener('input', function() {
    var query = this.value.toLowerCase();
    var results = document.querySelectorAll('#resultsoficon .resultoficon');
    var resultsContainer = document.getElementById('resultsoficon');
    var hasVisibleResults = false;

    results.forEach(function(result) {
        var text = result.textContent.toLowerCase();
        if (text.includes(query)) {
            result.classList.remove('hiddenoficon');
            hasVisibleResults = true;
        } else {
            result.classList.add('hiddenoficon');
        }
    });

    if (query.length > 0 && hasVisibleResults) {
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
});

document.getElementById('searchBoxoficon').addEventListener('focus', function() {
    if (this.value.length > 0) {
        document.getElementById('resultsoficon').style.display = 'block';
    }
});

document.getElementById('searchBoxoficon').addEventListener('blur', function() {
    setTimeout(function() {
        document.getElementById('resultsoficon').style.display = 'none';
    }, 200);
});

document.getElementById('resultsoficon').addEventListener('mousedown', function(e) {
    e.preventDefault();
});
// -----// fin BUSQUEDA OFICIOS //-----

//
// !!!!!! ADVERTENCIA: TODO ESTO ES PARA CONCEPTOS !!!!!!!!
//