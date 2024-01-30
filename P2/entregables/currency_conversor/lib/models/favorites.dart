import 'dart:convert';
import 'dart:io';
import 'package:currency_conversor/models/catalog.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class FavoritesModel extends ChangeNotifier {
  final List<Currency> _favorites = [];
  late bool connSuccess;
  late Currency _changedCurrency;
  final Map<String, Future<void>?> futures = {};

  FavoritesModel() {
    CatalogModel catalog = CatalogModel();
    catalog.initCurrencies.whenComplete((){
    //add(catalog.getByPosition(35));
    //add(catalog.getByPosition(116));
    add(catalog.getByPosition(0));
    add(catalog.getByPosition(1));
    });
    
  }

  void updateCurrencyValue(Currency currency, String newValue) {
    connSuccess = true;
    currency.setValue(newValue);
    _changedCurrency = currency;
    _favorites.remove(currency);
    _favorites.insert(0, currency);

    if (_favorites.length != 1) {
      if (changedCurrency.getValue() == "0.00") {
        updateAllToZero();
      } else {
        Future<void> updateFuture = _changeCurrenciesValue();

        futures.updateAll((key, value) => updateFuture);
      }
      notifyListeners();
    }
  }

  Currency get changedCurrency => _changedCurrency;

  List<Currency> get favorites => _favorites;

  Currency getByPosition(int position) {
    return _favorites[position];
  }

  void add(Currency currency) {
    connSuccess = true;
    if (_favorites.isEmpty) {
      _changedCurrency = currency;
      futures[currency.code] = null;
      _favorites.add(currency);
    } else {
      _favorites.add(currency);
      if (changedCurrency.getValue() == "0.00") {
        futures[currency.code] = null;
      } else {
        futures[currency.code] = _changeCurrencyValue(currency);
        //Cambio de connSucces
      }
    }
    notifyListeners();
  }

  void remove(Currency currency) {
    _favorites.remove(currency);
    futures.remove(currency.code);
    currency.setValue("0.00");
    notifyListeners();
  }

  Future<void> _changeCurrenciesValue() async {
    String request = "";
    for (var curr in _favorites) {
      request = "$request${_changedCurrency.code}/${curr.code},";
    }
    request = request.substring(0, request.length - 1);
    var uri = Uri(
        scheme: 'https',
        host: 'fcsapi.com',
        path: "/api-v3/forex/latest",
        queryParameters: {
          'symbol': request,
          'access_key': 'VRjTBRsojEyWjtmTJwgADgz',
        });

    try {
      var response = await http.get(uri);
      if (response.statusCode == 200) {
        var dataAsDartMap = jsonDecode(response.body);
        if (dataAsDartMap["status"] == true) {
          List exchangeRateList = dataAsDartMap["response"];
          int fav = 0;
          while (exchangeRateList.isNotEmpty) {
            String codeWithBar = exchangeRateList.first["s"];
            String code = codeWithBar.split("/").last;
            if (_favorites[fav].code.compareTo(_changedCurrency.code) == 0) {
              fav++;
            } else if (_favorites[fav].code.compareTo(code) != 0) {
              _favorites[fav].setValue("N/A");
              fav++;
            } else {
              double exchangeRate = double.parse(exchangeRateList.first["c"]);
              double calculatedChange =
                  exchangeRate * double.parse(changedCurrency.getValue());
              _favorites[fav].setValue(calculatedChange.toStringAsFixed(2));
              fav++;
              exchangeRateList.removeAt(0);
            }
          }
          for (var i = fav; i < _favorites.length; i++) {
            if (_changedCurrency.code.compareTo(_favorites[i].code) != 0) {
              _favorites[i].setValue("N/A");
            }
          }
        } else {
          for (var i = 0; i < _favorites.length; i++) {
            if (_changedCurrency.code.compareTo(_favorites[i].code) != 0) {
              _favorites[i].setValue("N/A");
            }
          }
        }
      } else {
        //error servidor
        connSuccess = false;
      }
    } catch (e) {
      //conexion fallida
      connSuccess = false;
    }
  }

  Future<void> _changeCurrencyValue(Currency curr) async {
    String request = "${_changedCurrency.code}/${curr.code}";

    var uri = Uri(
        scheme: 'https',
        host: 'fcsapi.com',
        path: "/api-v3/forex/latest",
        queryParameters: {
          'symbol': request,
          'access_key': '6qh23GFiWm9JNXMrqwFlNdj',
        });
    try {
      var response = await http.get(uri);
      if (response.statusCode == 200) {
        var dataAsDartMap = jsonDecode(response.body);
        if (dataAsDartMap["status"] == true) {
          var exchangeRateList = dataAsDartMap["response"];
          var exchangeRates = exchangeRateList[0];
          var exchangeRate = double.parse(exchangeRates["c"]);
          double calculatedChange =
              exchangeRate * double.parse(changedCurrency.getValue());
          curr.setValue(calculatedChange.toStringAsFixed(2));
        } else {
          curr.setValue("N/A");
        }
      } else {
        connSuccess = false;
      }
    } catch (e) {
      connSuccess = false;
    }
  }

  void updateAllToZero() {
    for (var curr in _favorites) {
      curr.setValue("0.00");
    }
  }
}
