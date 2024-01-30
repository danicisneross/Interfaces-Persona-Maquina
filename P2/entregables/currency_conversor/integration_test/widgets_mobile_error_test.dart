import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:currency_conversor/main.dart' as app;

void main() {
  testWidgets('Verify that errors occur', (WidgetTester tester) async {
    //Iniciamos la app
    app.main();

    //Espera que todos los elementos se carguen
    await tester.pumpAndSettle();

    //Cambiamos el valor de la primera moneda
    final textFieldEUR = find.byKey(const ValueKey('textFieldEUR'));
    expect(textFieldEUR, findsOneWidget);
    await tester.enterText(textFieldEUR, '1');
    await tester.pumpAndSettle();

    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    //Verificamos que sale popup del error
    expect(find.text('Connection Error'), findsOneWidget);

    //Click Ok en popup del error
    final ok = find.text('OK');
    await tester.tap(ok);
    await tester.pumpAndSettle();

    //Click en edit
    final edit = find.byKey(const ValueKey('edit'));
    await tester.tap(edit);
    await tester.pumpAndSettle();

    //Intentamos añadir una moneda
    final checkBoxGBP = find.byKey(const ValueKey('checkBoxGBP'));
    await tester.tap(checkBoxGBP);
    await tester.pumpAndSettle();

    //Verificamos que sale popup del error
    expect(find.text('Connection Error'), findsOneWidget);
  });
}
