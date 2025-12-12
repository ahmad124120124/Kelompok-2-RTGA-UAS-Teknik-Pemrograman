<?php

$host = "localhost";
$user = "root";
$pass = "";
$db   = "perpustakaan";

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) die("Koneksi gagal: " . $conn->connect_error);

function getBooks() { global $conn; return $conn->query("SELECT * FROM buku ORDER BY id_buku"); }
function addBook($j,$p,$t,$s){global $conn; $stmt=$conn->prepare("INSERT INTO buku(judul,penulis,tahun_terbit,jumlah_stok) VALUES(?,?,?,?)");$stmt->bind_param("ssii",$j,$p,$t,$s);return $stmt->execute();}
function deleteBook($id){global $conn; return $conn->query("DELETE FROM buku WHERE id_buku=$id");}

function getMembers(){ global $conn; return $conn->query("SELECT * FROM anggota ORDER BY id_anggota"); }
function addMember($n,$a,$t){global $conn; $stmt=$conn->prepare("INSERT INTO anggota(nama,alamat,no_telp) VALUES(?,?,?)");$stmt->bind_param("sss",$n,$a,$t); return $stmt->execute();}
function deleteMember($id){global $conn; return $conn->query("DELETE FROM anggota WHERE id_anggota=$id");}

function borrowBook($b,$a,$tgl){
    global $conn;
    $cek = $conn->query("SELECT jumlah_stok FROM buku WHERE id_buku=$b")->fetch_assoc();
    if ($cek['jumlah_stok'] <= 0) return "Stok habis";
    $conn->query("UPDATE buku SET jumlah_stok = jumlah_stok - 1 WHERE id_buku=$b");
    $stmt = $conn->prepare("INSERT INTO peminjaman (id_buku,id_anggota,tanggal_pinjam,status) VALUES (?,?,?,'Dipinjam')");
    $stmt->bind_param("iis",$b,$a,$tgl); $stmt->execute();
    return "Peminjaman Berhasil!";
}
  
 function returnBook($id,$tgl){
    global $conn;
    $p = $conn->query("SELECT * FROM peminjaman WHERE id_pinjam=$id")->fetch_assoc();
    if ($p['status']=="Kembali") return "Sudah dikembalikan!";
    $conn->query("UPDATE buku SET jumlah_stok = jumlah_stok + 1 WHERE id_buku=".$p['id_buku']);
    $stmt=$conn->prepare("UPDATE peminjaman SET status='Kembali',tanggal_kembali=? WHERE id_pinjam=?");
    $stmt->bind_param("si",$tgl,$id); $stmt->execute();
    return "Pengembalian Berhasil!";
}

function getLoans(){ global $conn;
    return $conn->query("
        SELECT p.*, b.judul, a.nama
        FROM peminjaman p
        JOIN buku b ON p.id_buku=b.id_buku
        JOIN anggota a ON p.id_anggota=a.id_anggota
        ORDER BY id_pinjam DESC
    ");
}

$page = $_GET['page'] ?? 'home';
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sistem Perpustakaan</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
  <div class="container">
    <a class="navbar-brand" href="?page=home">Perpustakaan</a>
    <div>
      <a class="btn btn-light me-2" href="?page=buku">Buku</a>
      <a class="btn btn-light me-2" href="?page=anggota">Anggota</a>
      <a class="btn btn-light" href="?page=transaksi">Transaksi</a>
    </div>
  </div>
</nav>

<div class="container">

<?php

if ($page == "home"): ?>
    <div class="p-5 bg-white shadow-sm rounded">
        <h2>Selamat Datang 👋</h2>
        <p class="mt-3">Gunakan menu di atas untuk mengelola buku, anggota, dan transaksi peminjaman.</p>
    </div>
<?php endif; ?>


<?php

if ($page == "buku"):

if (isset($_POST['tambah'])) addBook($_POST['judul'],$_POST['penulis'],$_POST['tahun'],$_POST['stok']);
if (isset($_POST['hapus'])) deleteBook($_POST['id']);
?>

<h2 class="mb-3">Manajemen Buku</h2>

<div class="card mb-4">
  <div class="card-header bg-success text-white">Tambah Buku</div>
  <div class="card-body">
    <form method="post">
        <div class="row g-2">
            <div class="col"><input class="form-control" name="judul" placeholder="Judul"></div>
            <div class="col"><input class="form-control" name="penulis" placeholder="Penulis"></div>
            <div class="col"><input class="form-control" type="number" name="tahun" placeholder="Tahun"></div>
            <div class="col"><input class="form-control" type="number" name="stok" placeholder="Stok"></div>
            <div class="col"><button class="btn btn-success" name="tambah">Tambah</button></div>
        </div>
    </form>
  </div>
</div>

<table class="table table-striped table-bordered shadow-sm">
    <tr class="table-primary">
        <th>ID</th><th>Judul</th><th>Penulis</th><th>Tahun</th><th>Stok</th><th>Aksi</th>
    </tr>

    <?php $data = getBooks(); while ($b = $data->fetch_assoc()): ?>
    <tr>
        <td><?= $b['id_buku'] ?></td>
        <td><?= $b['judul'] ?></td>
        <td><?= $b['penulis'] ?></td>
        <td><?= $b['tahun_terbit'] ?></td>
        <td><?= $b['jumlah_stok'] ?></td>
        <td>
            <form method="post" onsubmit="return confirm('Hapus buku ini?');">
                <input type="hidden" name="id" value="<?= $b['id_buku'] ?>">
                <button class="btn btn-danger btn-sm" name="hapus">Hapus</button>
            </form>
        </td>
    </tr>
    <?php endwhile; ?>
</table>
<?php endif; ?>


<?php

if ($page == "anggota"):

if (isset($_POST['tambah'])) addMember($_POST['nama'],$_POST['alamat'],$_POST['telp']);
if (isset($_POST['hapus'])) deleteMember($_POST['id']);
?>

<h2 class="mb-3">Manajemen Anggota</h2>

<div class="card mb-4">
  <div class="card-header bg-info text-white">Tambah Anggota</div>
  <div class="card-body">
    <form method="post">
        <div class="row g-2">
            <div class="col"><input class="form-control" name="nama" placeholder="Nama"></div>
            <div class="col"><input class="form-control" name="alamat" placeholder="Alamat"></div>
            <div class="col"><input class="form-control" name="telp" placeholder="No Telp"></div>
            <div class="col"><button class="btn btn-info" name="tambah">Tambah</button></div>
        </div>
    </form>
  </div>
</div>

<table class="table table-striped table-bordered shadow-sm">
    <tr class="table-primary">
        <th>ID</th><th>Nama</th><th>Alamat</th><th>Telepon</th><th>Aksi</th>
    </tr>

    <?php $data = getMembers(); while ($m = $data->fetch_assoc()): ?>
    <tr>
        <td><?= $m['id_anggota'] ?></td>
        <td><?= $m['nama'] ?></td>
        <td><?= $m['alamat'] ?></td>
        <td><?= $m['no_telp'] ?></td>
        <td>
            <form method="post" onsubmit="return confirm('Hapus anggota ini?');">
                <input type="hidden" name="id" value="<?= $m['id_anggota'] ?>">
                <button class="btn btn-danger btn-sm" name="hapus">Hapus</button>
            </form>
        </td>
    </tr>
    <?php endwhile; ?>
</table>
<?php endif; ?>
 