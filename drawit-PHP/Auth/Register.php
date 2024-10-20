<?php
// Include database connection
require '../Config/db_connect.php';

$name = $email = "";
$nameErr = $emailErr = $successMessage = $errorMessage = "";

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (empty($_POST['name'])) {
        $nameErr = "Name is required";
    } else {
        $name = filter_var($_POST['name'], FILTER_SANITIZE_STRING);
    }

    if (empty($_POST['email'])) {
        $emailErr = "Email is required";
    } else {
        $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $emailErr = "Invalid email format";
        }
    }

    if (empty($nameErr) && empty($emailErr)) {
        try {
            // Check if email is already registered
            $stmt = $conn->prepare("SELECT COUNT(*) FROM user WHERE Email = :email");
            $stmt->execute([':email' => $email]);
            $emailCount = $stmt->fetchColumn();

            if ($emailCount > 0) {
                $emailErr = "Email is already registered";
            } else {
                // Prepare the SQL statement with named placeholders
                $stmt = $conn->prepare("INSERT INTO user (Name, Email, DateCreated) VALUES (:name, :email, NOW())");
                // Execute the statement with an associative array of parameters
                $stmt->execute([':name' => $name, ':email' => $email]);
                $successMessage = "Registration successful!";
            }
        } catch (PDOException $e) {
            $errorMessage = "Error: " . $e->getMessage();
        }
    }
}

$conn = null;
?>


<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/x-icon" href="../assets/icon/icon-500x500.png" width="500" height="500">
    <title>Registeration Form</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="../assets/css/style.css">
</head>

<body>

    <!-- Navbar -->

    <nav class="navbar fixed-top">
        <div class="container-fluid" style="padding: 20px 60px 0px 60px;">
            <div class="d-flex justify-content-center align-items-center" id="icon">
                <img src="../assets/icon/icon-500x500.png" width="40" height="40" alt="">
                <a class="navbar-brand fw-bold h-3 pb-0">Drawit</a>
            </div>
            <div style="display: flex; flex-direction: row; justify-self: center; align-items: center;">
                <p style="margin-bottom: 0px; color: rgb(69, 69, 69);">Already have an account ? <a href=""
                        class=" text-decoration-none fw-bold" type="submit">Sign in -></a></p>
            </div>
        </div>
    </nav>

    <!-- Main-body -->

    <div class="text-center"
        style="height: 95vh; display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div class="front-bg d-flex align-items-center justify-content-center">
            <div class="rounded-4 shadow shadow-3 p-3 bg-white" style=" width: 40%; height: 75%; margin-top:100px;">
                <h2 class="p-4 mb-4 ">Registration Form</h2>
                <?php if ($successMessage): ?>
                    <p style="color:green;"><?php echo $successMessage; ?></p>
                <?php endif; ?>
                <?php if ($errorMessage): ?>
                    <p style="color:red;"><?php echo $errorMessage; ?></p>
                <?php endif; ?>
                <form method="post" action="">
                    <div class="m-3 ps-5 pe-5">
                        <!-- <label for="formName" class="form-label">Name :</label> -->
                        <input class="form-control" type="text" name="name" id="formName"
                            placeholder="Enter Full Name" value="<?php echo htmlspecialchars($name); ?>">
                    </div>
                    <span style="color:red;"><?php echo $nameErr; ?></span><br>
                    <div class="m-3 ps-5 pe-5">
                        <!-- <label for="formEmail" class="form-label">Email :</label> -->
                        <input class="form-control" type="email" name="email" id="formEmail"
                            placeholder="Enter Email" value="<?php echo htmlspecialchars($email); ?>">
                        <span style="color:red;"><?php echo $emailErr; ?></span><br>
                        <button class="btn btn-lg btn-dark p-2 ps-4 pe-4 m-4" type="submit">Register</button>
                </form>
            </div>
        </div>
    </div>

    <!-- footer -->
    <div>
        <div class="d-flex justify-content-center p-5">
            <img src="../assets/icon/icon-500x500.png" width="40" height="40" alt="">
            <a class="text-decoration-none fs-6 text-secondary p-3 " href="">Drawit</a>
            <a class="text-decoration-none fs-6 text-secondary p-3 " href="">Terms</a>
            <a class="text-decoration-none fs-6 text-secondary p-3 " href="">Privacy Policy</a>
            <a class="text-decoration-none fs-6 text-secondary p-3 " href="">Docs</a>
            <a class="text-decoration-none fs-6 text-secondary p-3 " href="">Security</a>
            <a class="text-decoration-none fs-6 text-secondary p-3 " href="">Contacts</a>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous">
        </script>
</body>

</html>