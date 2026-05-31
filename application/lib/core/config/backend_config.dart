class BackendConfig {
  const BackendConfig._();

  static const baseUrl = String.fromEnvironment(
    'BACKEND_BASE_URL',
    defaultValue: 'http://192.168.1.102:8000',
  );

  static const predictPath = '/api/v1/predict';
  static const frameFieldName = 'frame';
  static const predictionInterval = Duration(milliseconds: 200);
  static const timeout = Duration(seconds: 5);
}
