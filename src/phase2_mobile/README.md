# EchoEcho-T Android preview

Flutter UI scaffold with generated Pigeon interfaces. The native translation
engine and Bluetooth routing are not implemented. Startup failure is displayed
in the UI; a successful debug build does not imply working translation.

Validated tooling: Flutter 3.44.7, Dart 3.12.2, Java 17.

```sh
flutter pub get --enforce-lockfile
flutter analyze
flutter test
flutter build apk --debug
```

Release builds do not use debug signing. Configure private production signing
before distribution. See [the QA and code review report](../../docs/PRODUCTION_READINESS.md)
for remaining implementation and device validation requirements.
