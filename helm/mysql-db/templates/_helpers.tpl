{{- define "mysql-quizdb.name" -}}
user-db
{{- end }}

{{- define "mysql-quizdb.fullname" -}}
{{ include "mysql-quizdb.name" . }}
{{- end }}

{{- define "mysql-quizdb.labels" -}}
app: user-db
{{- end }}