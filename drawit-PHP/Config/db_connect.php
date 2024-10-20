<?php
// Securely load database credentials from a separate configuration file
require 'config.php';

try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    // Set PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // Use UTF-8 encoding for the connection
    $conn->exec("set names utf8");
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}
?>
