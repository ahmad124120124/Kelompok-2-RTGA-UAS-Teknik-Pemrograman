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
 