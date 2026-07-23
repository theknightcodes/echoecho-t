import '../services/echoecho_api.g.dart';

class PipelineStatus {
  const PipelineStatus({this.stage = PipelineStage.idle, this.message});

  final PipelineStage stage;
  final String? message;

  PipelineStatus copyWith({PipelineStage? stage, String? message}) {
    return PipelineStatus(
      stage: stage ?? this.stage,
      message: message ?? this.message,
    );
  }
}
