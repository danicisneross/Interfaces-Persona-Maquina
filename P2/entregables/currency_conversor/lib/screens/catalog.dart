import 'package:currency_conversor/main.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:currency_conversor/models/catalog.dart';
import 'package:currency_conversor/models/favorites.dart';

class MyCatalog extends StatefulWidget {
  const MyCatalog({super.key});
  @override
  State<StatefulWidget> createState() => _MyCatalog();
}

class _MyCatalog extends State<MyCatalog> {
  final CatalogModel catalog = CatalogModel();
  _MyCatalog();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder(
        future: catalog.initCurrencies,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            return CustomScrollView(
              key: const ValueKey("catalogList"),
              slivers: [
                _MyAppBar(),
                const SliverToBoxAdapter(child: SizedBox(height: 12)),
                SliverList(
                  delegate: SliverChildBuilderDelegate((context, index) {
                    if (catalog.currencies.isNotEmpty &&
                        index < catalog.currencies.length) {
                      return _MyListItem(catalog.getByPosition(index));
                    }
                    return null;
                  }),
                )
              ],
            );
          }
        },
      ),
    );
  }
}

class _AddButton extends StatelessWidget {
  final Currency currency;

  const _AddButton({required this.currency});

  @override
  Widget build(BuildContext context) {
    var isInFavorites = context.select<FavoritesModel, bool>(
      (favoriteList) => favoriteList.favorites.contains(currency),
    );

    return Checkbox(
      key: ValueKey("checkBox${currency.code}"),
      checkColor: Colors.white,
      activeColor: Colors.green,
      value: isInFavorites,
      onChanged: isInFavorites
          ? (bool? value) {
              var favoriteList = context.read<FavoritesModel>();
              favoriteList.remove(currency);
            }
          : (bool? value) {
              var favoriteList = context.read<FavoritesModel>();
              favoriteList.add(currency);
              favoriteList.futures[currency.code]?.whenComplete(() {
                if (!favoriteList.connSuccess) {
                  showDialog<String>(
                    context: context,
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
                  favoriteList.remove(currency);
                }
              });
            },
    );
  }
}

class _MyAppBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SliverAppBar(
      title: Text('Catalog', style: Theme.of(context).textTheme.displayLarge),
      floating: true,
      actions: [
        if (MediaQuery.of(navigatorKey.currentState!.context).size.width < 600)
          IconButton(
            color: Colors.green,
            iconSize: 35,
            onPressed: () => context.go('/favorites'),
            icon: const Icon(Icons.done),
            key: const ValueKey("okButton"),
          )
      ],
      automaticallyImplyLeading: false,
    );
  }
}

class _MyListItem extends StatelessWidget {
  final Currency currency;
  const _MyListItem(this.currency);

  @override
  Widget build(BuildContext context) {
    var textTheme = Theme.of(context).textTheme.titleLarge;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: LimitedBox(
        maxHeight: 60,
        child: Row(children: [
          currency.flag,
          const SizedBox(width: 24),
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
              Expanded(
                child: Text(
                  currency.name,
                  style: Theme.of(context).textTheme.displayMedium,
                ),
              ),
            ],
          ),
          const Spacer(),
          _AddButton(currency: currency)
        ]),
      ),
    );
  }
}
