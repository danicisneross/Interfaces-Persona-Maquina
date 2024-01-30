import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class CatalogModel {
  static final CatalogModel _instance = CatalogModel._internal();
  List<Currency> currencies = [];
  late Future<void> initCurrencies;

  Future<void> _initCurrencyList() async {
    // Cargar el contenido del archivo JSON
    String jsonString = await rootBundle.loadString('assets/flag_code.json');
    var data = jsonDecode(jsonString);
    var dataList = data["currencies"];
    for (var currency in dataList) {
      String str = currency['flag'];
      var splitted = str.split(',');
      currencies.add(Currency(currency['code'], currency['name'], splitted[1]));
    }
  }

  factory CatalogModel() {
    return _instance;
  }

  CatalogModel._internal() {
    initCurrencies = _initCurrencyList();
  }

  Currency getByPosition(int position) {
    return currencies[position];
  }
}

class Currency {
  final String code;
  final String name;
  late final Image flag;
  late String _value = "0.00";

  Currency(this.code, this.name, String base64String) {
    flag = Image.memory(base64Decode(base64String));
  }

  void setValue(String newValue) {
    _value = newValue;
  }

  String getValue() {
    return _value;
  }
}
