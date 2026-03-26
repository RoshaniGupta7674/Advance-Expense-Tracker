const ctx = document.getElementById('expenseChart');

new Chart(ctx, {

type: 'bar',

data: {

labels: ['Food','Travel','Shopping','Bills','Rent'],

datasets: [{
label: 'Expenses',

data: [500,300,200,400,800]

}]

},

options: {

responsive:true

}

});