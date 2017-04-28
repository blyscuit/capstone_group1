<?php
	// $file_result ="";
	// if($_FILES["file"]["error"]>0)
	// {
	// 	$file_result .="No File Uploaded or Invalid File";
	// 	$file_result .="Error Code:".$_FILES["file"]["error"];
	// } else{
	// 	$file_result .=
	// 	"upload:" .$_FILES["file"]["name"] . "<br>".
	// 	"type:" .$_FILES["file"]["type"] . "<br>".
	// 	"size:" .($_FILES["file"]["size"]/1024) . "<br>".
	// 	"temp file:".$_FILES["file"]["tmp_name"] . "<br>";

	// 	move_uploaded_file($_FILES["file"]["tmp_name"], "\upload");
	// 	$file_result .= "File Uploaded";
	// }

if(isset($_FILES['file'])){
	$file = $_FILES['file'];
	
	$file_name =$file['name'];
	$file_tmp =$file['tmp_name'];
	$file_size =$file['size'];
	$file_error =$file['error'];

	$file_ext = explode('.', $file_name);
	$file_ext = strtolower(end($file_ext));
	$allowed = array('txt', 'png', 'jpg');
	if(in_array($file_ext, $allowed)){
		if($file_error ===0){
			if($file_size <= 2097152){
				 $file_name_new = uniqid('', true) . '.' . $file_ext;





				$file_destination = 'upload/' . $file_name_new;

				if(move_uploaded_file($file_tmp, $file_destination)){
					 echo $file_destination;
					echo " uploaded";
					// use the code below to go back to main page
				  //header('Location: '. "//snowywords2.ddns.net:7777/kaidee/"); 
					//the code below for going to the uploaded pic
				header('Location: '. "//snowywords2.ddns.net:7777/kaidee/result.html");
				}
			}
		}
	}
	
}

?>