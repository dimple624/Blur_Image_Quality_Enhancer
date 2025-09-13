import 'package:flutter/material.dart';
import 'dart:io';

class ResultScreen extends StatelessWidget {
  final String imagePath;
  ResultScreen({required this.imagePath});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Enhanced Image')),
      body: Center(
        child: Image.file(File(imagePath)),
      ),
    );
  }
}
