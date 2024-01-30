import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:currency_conversor/main.dart' as app;

import 'tools.dart';

void main() {
  testWidgets(
      'verify coversion through favorites screen',
      (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    //Vamos a catalogo
    final edit = find.byKey(const ValueKey('edit'));
    await tester.tap(edit);
    await tester.pumpAndSettle();

    /*AÑADIR MONEDA SIN CONVERSIÓN*/

    //Scroll buscando la moneda que no existe
    //final listFinder = find.byType(Scrollable);
    final listFinder = find.byType(Scrollable);
    final checkBoxKGS = find.byKey(const ValueKey('checkBoxKGS'));

    await tester.scrollUntilVisible(
      checkBoxKGS,
      200.0,
      scrollable: listFinder,
    );

    await tester.pumpAndSettle();
    //Hacemos tap en la moneda que no existe y la añadimos a favoritos
    await tester.tap(checkBoxKGS);
    await tester.pumpAndSettle();

    await tester.drag(find.byType(CustomScrollView), const Offset(0.0, 5000.0));
    await tester.pumpAndSettle();

    //Le damos al bonton de OK y volvemos a Favorites, aqui deberiamos tener 3 monedas
    final okButton = find.byKey(const ValueKey('okButton'));
    await tester.tap(okButton);
    await tester.pumpAndSettle();

    //Le damos al TextField de la primera moneda y escribimos un numero
    final textFieldEUR = find.byKey(const ValueKey('textFieldEUR'));
    await tester.enterText(textFieldEUR, '1');
    await tester.pumpAndSettle();

    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    //Todas las monedas deben actualizarse
    String convertedValue1 = await requestAPI("EUR", "USD", 1.0);
    expect(find.text(convertedValue1), findsOneWidget);

    String convertedValue3 = await requestAPI("EUR", "KGS", 1.0);
    expect(find.text(convertedValue3), findsOneWidget);
  });

  testWidgets(
      'verify coversion through adding currencies',
      (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    //Le damos al TextField de la primera moneda y escribimos un numero
    final textFieldEUR = find.byKey(const ValueKey('textFieldEUR'));
    await tester.enterText(textFieldEUR, '1');
    await tester.pumpAndSettle();

    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    //Vamos a catalogo
    final edit = find.byKey(const ValueKey('edit'));
    await tester.tap(edit);
    await tester.pumpAndSettle();

    //Añadimos monedas
    final checkBoxGBP = find.byKey(const ValueKey('checkBoxGBP'));
    await tester.tap(checkBoxGBP);
    await tester.pumpAndSettle();

    
    final listFinder = find.byType(Scrollable);
    final checkBoxKGS = find.byKey(const ValueKey('checkBoxKGS'));

    await tester.scrollUntilVisible(
      checkBoxKGS,
      200.0,
      scrollable: listFinder,
    );
    await tester.pumpAndSettle();

    await tester.tap(checkBoxKGS);
    await tester.pumpAndSettle();

    await tester.drag(find.byType(CustomScrollView), const Offset(0.0, 5000.0));
    await tester.pumpAndSettle();

    //Le damos al bonton de OK y volvemos a Favorites
    final okButton = find.byKey(const ValueKey('okButton'));
    await tester.tap(okButton);
    await tester.pumpAndSettle();

    String convertedValue2 = await requestAPI("EUR", "GBP", 1.0);
    expect(find.text(convertedValue2), findsOneWidget);
    
    String convertedValue3 = await requestAPI("EUR", "KGS", 1.0);
    expect(find.text(convertedValue3), findsOneWidget);
  });


  testWidgets('verify we can add a currency to favorites', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    //Le damos al TextField de la primera moneda y escribimos un numero
    final edit = find.byKey(const ValueKey('edit'));
    await tester.tap(edit);
    await tester.pumpAndSettle();

    //En catalogo, presionamos sobre el checkbox de una moneda para añadirla a Favoritos
    final checkBoxGBP = find.byKey(const ValueKey('checkBoxGBP'));
    await tester.tap(checkBoxGBP);
    await tester.pumpAndSettle();

    //Le damos al bonton de OK y volvemos a Favorites, aqui deberiamos tener 3 monedas
    final okButton = find.byKey(const ValueKey('okButton'));
    await tester.tap(okButton);
    await tester.pumpAndSettle();

    //Verificamos que estás las dos nuevas monedas
    final favoritesGBP = find.byKey(const ValueKey('favoritesGBP'));
    expect(favoritesGBP, findsOneWidget);
  });

  testWidgets('verify that we can remove currency of favorites',
      (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    /*ELIMINAR MONEDA*/

    //Presionamos el widget de editar --> catalogo
    final edit = find.byKey(const ValueKey('edit'));
    await tester.tap(edit);
    await tester.pumpAndSettle();

    //En catalogo, presionamos sobre el checkbox de una moneda que ya esta marcada para quitarla de Favoritos
    final checkBoxUSD = find.byKey(const ValueKey('checkBoxUSD'));
    await tester.tap(checkBoxUSD);
    await tester.pumpAndSettle();

    //Le damos al bonton de OK y volvemos a Favorites, ahora la moneda no deberia estar
    final okButton = find.byKey(const ValueKey('okButton'));
    await tester.tap(okButton);
    await tester.pumpAndSettle();

    //solo hay 1 moneda (la que esta por defecto)
    final favoritesEUR = find.byKey(const ValueKey('favoritesEUR'));
    expect(favoritesEUR, findsOneWidget);
  });
}
