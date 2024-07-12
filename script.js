const navbarToggle = document.querySelector('.navbar-toggle');
const navbarMenu = document.querySelector('.navbar ul');

navbarToggle.addEventListener('click', () => {
    navbarMenu.classList.toggle('active');
});
// Ambil referensi tabel berdasarkan ID
var table = document.getElementById("myTable");

// Buat data yang ingin ditambahkan
var data = [
  { name: "Mark Johnson", age: 28, country: "Australia" },
  { name: "Anna Smith", age: 32, country: "Germany" }
];

// Loop melalui data dan tambahkan ke tabel
data.forEach(function(item) {
  // Buat sebuah baris baru
  var row = table.insertRow();

  // Masukkan sel-sel ke dalam baris
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  var cell3 = row.insertCell(2);

  // Isi sel dengan data
  cell1.textContent = item.name;
  cell2.textContent = item.age;
  cell3.textContent = item.country;
});



