import 'package:currency_conversor/common/theme.dart';
import 'package:currency_conversor/models/favorites.dart';
import 'package:currency_conversor/screens/catalog.dart';
import 'package:currency_conversor/screens/favorites.dart';
import 'package:currency_conversor/screens/homePageIPad.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:flutter/material.dart';

final navigatorKey = GlobalKey<NavigatorState>();
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => FavoritesModel(),
      child: const MyApp(),
    ),
  );
}


GoRouter router(String routeHome) {
  return GoRouter(
    navigatorKey: navigatorKey,
    initialLocation: routeHome,
    routes: [
      if(routeHome == '/favorites')
        GoRoute(
          path: '/favorites',
          builder: (context, state) => const MyFavorites(),
          routes: [
            GoRoute(
              path: 'catalog',
              builder: (context, state) => const MyCatalog(),
            )
          ],
        ),
      if(routeHome == '/homePageIPad')
        GoRoute(
        path: '/homePageIPad',
        builder: (context, state) => const MyHomePageIpad(),
      )
    ],
  );
} 


class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    String routeHome;
    
    if (MediaQuery.of(context).size.width < 600) {
      routeHome = '/favorites';
    } else {
      routeHome = '/homePageIPad';
    }

    return MaterialApp.router(
      title: 'Flutter Demo',
      theme: appTheme,
      routerConfig: router(routeHome),
    );
  }
}