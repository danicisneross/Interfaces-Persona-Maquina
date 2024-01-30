import 'package:currency_conversor/screens/catalog.dart';
import 'package:currency_conversor/screens/favorites.dart';
import 'package:flutter/material.dart';

class MyHomePageIpad extends StatefulWidget {
  const MyHomePageIpad({super.key});
  @override
  State<StatefulWidget> createState() => _MyHomePageIpad();
}

class _MyHomePageIpad extends State<MyHomePageIpad> {
  _MyHomePageIpad();

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: double.infinity,
      height: double.infinity,
      child: Row(
        children: [
          Expanded(child: MyFavorites()),
          VerticalDivider(),
          Expanded(child: MyCatalog()),
        ],
      ),
    );
  }
}
