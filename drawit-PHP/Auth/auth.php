<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

session_start();

require '../Config/db_connect.php';
require 'phpmailer/src/Exception.php';
require 'phpmailer/src/PHPMailer.php';
require 'phpmailer/src/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

function sendOtp($email)
{
    $otp = random_int(100000, 999999);
    $expiry = time() + 300; // 5 minutes from now

    // Store OTP and expiry time in session
    $_SESSION['otp'] = $otp;
    $_SESSION['otp_expiry'] = $expiry;
    $_SESSION['otp_email'] = $email;
    $_SESSION['otp_sent_time'] = time();

    $mail = new PHPMailer(true);

    try {
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com';
        $mail->SMTPAuth = true;
        $mail->Username = 'drawit.sidekick@gmail.com';
        $mail->Password = 'izounnemalhaxpvt';
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = 587;

        // Enable SMTP keep-alive
        $mail->SMTPKeepAlive = true;

        $mail->setFrom('drawit.sidekick@gmail.com', 'DrawIt Sidekick');
        $mail->addAddress($email);

        $mail->isHTML(true);
        $mail->Subject = 'Your OTP Code';
        $mail->Body = 'Your OTP code is: ' . $otp;

        $mail->send();
        return true;
    } catch (Exception $e) {
        return false;
    }
}

function destroyOtpSession()
{
    unset($_SESSION['otp']);
    unset($_SESSION['otp_expiry']);
    unset($_SESSION['otp_email']);
    unset($_SESSION['otp_sent_time']);
}


$response = array('status' => 'error', 'message' => 'Invalid request');

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $action = $_POST['action'];

    if ($action == 'send_otp') {
        $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);

        $stmt = $conn->prepare("SELECT UserID FROM user WHERE Email = :email");
        $stmt->bindParam(':email', $email);
        $stmt->execute();
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user) {
            $currentTime = time();
            if (!isset($_SESSION['otp_sent_time']) || $currentTime - $_SESSION['otp_sent_time'] > 120) { // 2 minutes resend restriction
                if (sendOtp($email)) {
                    $response = array('status' => 'success', 'message' => 'OTP sent successfully');
                } else {
                    $response = array('status' => 'error', 'message' => 'Failed to send OTP');
                }
            } else {
                $response = array('status' => 'error', 'message' => 'Please wait 2 minutes before resending the OTP');
            }
        } else {
            $response = array('status' => 'error', 'message' => 'Email is not registered');
        }
    } elseif ($action == 'verify_otp') {
        $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
        $otp = filter_var($_POST['otp'], FILTER_SANITIZE_STRING);

        if (isset($_SESSION['otp']) && $_SESSION['otp_email'] == $email && $_SESSION['otp'] == $otp && time() < $_SESSION['otp_expiry']) {
            // OTP is valid
            $_SESSION['user_logged_in'] = true;
            $_SESSION['user_email'] = $_SESSION['otp_email'];
            destroyOtpSession();
            $response = array('status' => 'success', 'message' => 'OTP verified successfully. User logged in.');
        } else {
            $response = array('status' => 'error', 'message' => 'Invalid or expired OTP');
        }
    }
}

header('Content-Type: application/json');
echo json_encode($response);
?>