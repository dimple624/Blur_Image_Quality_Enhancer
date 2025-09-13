import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html;

class ApiService {
  static const String _baseUrl = "http://127.0.0.1:5000"; // Update if hosted elsewhere
  final storage = FlutterSecureStorage();

  // User Registration
  Future<String?> register(String email, String password) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/register'),
      headers: {
        "Content-Type": "application/json",
      },
      body: json.encode({"email": email, "password": password}),
    );

    if (response.statusCode == 201) {
      return "Registration successful";
    } else if (response.statusCode == 400) {
      final data = json.decode(response.body);
      return data['message'] ?? "Registration failed";
    } else {
      return "Registration failed";
    }
  }

  // User Login
  Future<String?> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/login'),
      headers: {
        "Content-Type": "application/json",
      },
      body: json.encode({"email": email, "password": password}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      await storage.write(key: "access_token", value: data["access_token"]);
      return "Login successful";
    } else {
      return "Invalid credentials";
    }
  }

  // Upload Image and Enhance (for Web)
  Future<Map<String, String>> uploadImage(html.File imageFile, {String? token}) async {
    token ??= await storage.read(key: "access_token");
    if (token == null) {
      return {
        "message": "Please login first!",
        "url": "",
      };
    }

    final formData = html.FormData();
    formData.appendBlob("image", imageFile, imageFile.name);

    final request = html.HttpRequest();
    request.open("POST", '$_baseUrl/upload');
    request.responseType = 'json';
    request.setRequestHeader("Authorization", "Bearer $token");
    request.withCredentials = false;

    final completer = Completer<Map<String, String>>();

    request.onLoadEnd.listen((_) {
      if (request.status == 200) {
        final resp = request.response as Map;
        final downloadUrl = resp['download_url'] as String;
        completer.complete({
          "message": "Image enhanced successfully",
          "url": downloadUrl,
        });
      } else {
        String msg = "Upload failed with status ${request.status}";
        if (request.response is Map && (request.response as Map).containsKey('message')) {
          msg = (request.response as Map)['message'] as String;
        }
        completer.complete({
          "message": msg,
          "url": "",
        });
      }
    });

    request.onError.listen((_) {
      completer.complete({
        "message": "Network error during upload",
        "url": "",
      });
    });

    request.send(formData);
    return completer.future;
  }

  // Download Enhanced Image
  Future<String> downloadImageFromUrl(String url, String filename) async {
    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        final blob = html.Blob([response.bodyBytes.buffer.asUint8List()]);
        final tempUrl = html.Url.createObjectUrlFromBlob(blob);
        final anchor = html.AnchorElement(href: tempUrl)
          ..setAttribute("download", filename)
          ..click();
        html.Url.revokeObjectUrl(tempUrl);
        return "Download successful";
      } else {
        return "Failed to download image with status: ${response.statusCode}";
      }
    } catch (e) {
      return "Error downloading image: $e";
    }
  }
}
