import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'result_screen.dart';
import 'package:http/http.dart' as http;

class UploadScreen extends StatefulWidget {
  @override
  _UploadScreenState createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  File? _image;
  final picker = ImagePicker();

  Future<void> _pickImage() async {
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });
    }
  }

  Future<void> _uploadImage() async {
    var request = http.MultipartRequest('POST', Uri.parse('http://127.0.0.1:5000/upload'));
    request.files.add(await http.MultipartFile.fromPath('image', _image!.path));

    // If you're sending an authentication token:
    // request.headers.addAll({'Authorization': 'Bearer <JWT_TOKEN>'});

    var response = await request.send();

    if (response.statusCode == 200) {
      // Navigate to the result screen with the enhanced image
      Navigator.push(
          context, MaterialPageRoute(builder: (context) => ResultScreen(imagePath: _image!.path)));
    } else {
      // Handle error
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Upload failed!')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload Image')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            _image == null
                ? Text('No image selected.')
                : Image.file(_image!),
            ElevatedButton(
              onPressed: _pickImage,
              child: Text('Pick Image'),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _uploadImage,
              child: Text('Upload and Enhance'),
            ),
          ],
        ),
      ),
    );
  }
}
