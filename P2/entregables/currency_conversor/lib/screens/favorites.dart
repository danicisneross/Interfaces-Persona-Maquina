import 'package:currency_conversor/main.dart';
import 'package:currency_conversor/models/favorites.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:currency_conversor/models/catalog.dart';
import 'package:provider/provider.dart';

class MyFavorites extends StatelessWidget {
  const MyFavorites({super.key});

  @override
  Widget build(BuildContext context) {
    FavoritesModel myFavorites = context.watch<FavoritesModel>();
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          _MyAppBar(),
          const SliverToBoxAdapter(child: SizedBox(height: 12)),
          SliverList(
            delegate: SliverChildBuilderDelegate((context, index) {
              if (myFavorites.favorites.isNotEmpty &&
                  index < myFavorites.favorites.length) {
                return _MyListItem(myFavorites.getByPosition(index), index);
              } else {
                return null;
              }
            }),
          ),
        ],
      ),
    );
  }
}

class _MyAppBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SliverAppBar(
      title: Text('Favorites Currencies',
          style: Theme.of(context).textTheme.displayLarge),
      floating: true,
      actions: [
        if (MediaQuery.of(navigatorKey.currentState!.context).size.width < 600)
          IconButton(
              onPressed: () => context.go('/favorites/catalog'),
              icon: const Icon(Icons.mode_outlined),
              key: const ValueKey("edit"))
      ],
    );
  }
}

class MyTextField extends StatelessWidget {
  final Currency currency;
  final FavoritesModel myFavorites;
  const MyTextField(this.currency, this.myFavorites, {super.key});

  @override
  Widget build(BuildContext context) {
    TextEditingController myController =
        TextEditingController(text: currency.getValue());
    return SizedBox(
      width: 130,
      height: 40,
      key :  ValueKey("textField${currency.code}"),
      child: TextField(
        controller: myController,
        style: const TextStyle(fontSize: 20),
        decoration: const InputDecoration(
          isDense: true,
          contentPadding: EdgeInsets.fromLTRB(5.0, 1.0, 5.0, 1.0),
          border: OutlineInputBorder(),
        ),
        textAlignVertical: const TextAlignVertical(y: -0.8),
        keyboardType: TextInputType.number, // Tipo de teclado que se muestra
        inputFormatters: [
          //Solo dejar meter un determinado valor en el campo
          FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,2}')),
        ],
        onSubmitted: (value) {
          myFavorites.updateCurrencyValue(currency, value);
          if (myFavorites.futures[currency.code] != null) {
            myFavorites.futures[currency.code]?.whenComplete(() {
              if (!myFavorites.connSuccess) {
                showDialog<String>(
                  context: navigatorKey.currentState!.overlay!.context,
                  builder: (BuildContext context) => AlertDialog(
                    title: const Text('Connection Error'),
                    content: const Text('try again in a few minutes'),
                    actions: <Widget>[
                      TextButton(
                        onPressed: () => Navigator.pop(context, 'OK'),
                        child: const Text('OK'),
                      ),
                    ],
                  ),
                );
              }
            });
          }
        },
        onTap: () {
          // Borrar el contenido al tocar el TextField
          myController.text = "";
        },
        onTapOutside: (text) {
          if (myController.text.isEmpty) {
            myController.text = currency.getValue();
          }
        },
      ),
    );
  }
}

class FutureTextField extends StatelessWidget {
  final Currency currency;
  const FutureTextField({super.key, required this.currency});

  @override
  Widget build(BuildContext context) {
    FavoritesModel myFavorites = context.watch<FavoritesModel>();
    if (myFavorites.futures[currency.code] == null) {
      return MyTextField(currency, myFavorites);
    } else {
      return FutureBuilder(
          future: myFavorites.futures[currency.code],
          builder: (context, snapshot) {
            if (myFavorites.futures[currency.code] != null &&
                snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            } else if (myFavorites.futures[currency.code] != null &&
                snapshot.hasError) {
              return Center(child: Text('Error: ${snapshot.error}'));
            } else {
              return MyTextField(currency, myFavorites);
            }
          });
    }
  }
}

class _MyListItem extends StatelessWidget {
  final Currency currency;
  final int index;

  const _MyListItem(this.currency, this.index);

  @override
  Widget build(BuildContext context) {
    //var textTheme = Theme.(context).textTheme.titleLarge;

    return Padding(
        key:   ValueKey("favorites${currency.code}"),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: LimitedBox(
          maxHeight: 60,
          child: DecoratedBox(
            decoration: BoxDecoration(color: index == 0? const Color.fromARGB(26, 64, 64, 64) : const Color.fromARGB(255, 255, 253, 253),borderRadius: BorderRadius.circular(15.0), ),
            child: Row(
              children: [
                const SizedBox(width: 7),
                currency.flag,
                const SizedBox(width: 20),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      currency.code,
                      textAlign: TextAlign.left,
                      style: const TextStyle(
                        fontFamily: 'Corben',
                        fontWeight: FontWeight.w600,
                        fontSize: 11,
                        color: Colors.black,
                      ),
                    ),
                    SizedBox(
                      width: 150,
                      child: Text(
                        currency.name,
                        style: Theme.of(context).textTheme.displayMedium,
                      ),
                    )
                  ],
                ),
                const Spacer(),
                FutureTextField(currency: currency),
                const SizedBox(width: 7)
              ],
            ),
          ),
        )
        );
  }
}
