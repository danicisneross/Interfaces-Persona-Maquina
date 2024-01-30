import 'dart:convert';

import 'package:http/http.dart' as http;

Future<String> requestAPI (String currency1, String currency2, double value) async {
  String request = '$currency1/$currency2';
  var uri = Uri(
        scheme: 'https',
        host: 'fcsapi.com',
        path: "/api-v3/forex/latest",
        queryParameters: {
          'symbol': request,
          'access_key': 'L75v2fVdC1Ww6rwPPurnwP',
        });
  var response = await http.get(uri);
  var dataAsDartMap = jsonDecode(response.body);
  if (dataAsDartMap["status"] == true) {
    var exchangeRateList = dataAsDartMap["response"];
    var exchangeRates = exchangeRateList[0];
    var exchangeRate = double.parse(exchangeRates["c"]);
    double calculatedChange =
        exchangeRate * value;
    return calculatedChange.toStringAsFixed(2);
} else {
    return "N/A";
}
  


}