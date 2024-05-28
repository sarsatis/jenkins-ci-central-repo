#!/bin/bash

# Define variables
CERT_FILES=("path/to/cert1.p12" "path/to/cert2.p12" "path/to/cert3.p12" "path/to/cert4.p12" "path/to/cert5.p12" "path/to/cert6.p12" "path/to/cert7.p12" "path/to/cert8.p12" "path/to/cert9.p12" "path/to/cert10.p12")
SECRET_NAME_PREFIX="my-tls-secret"
NAMESPACE="default"

# Loop over each certificate file
for CERT_FILE_PATH in "${CERT_FILES[@]}"; do
  if [[ ! -f "$CERT_FILE_PATH" ]]; then
    echo "Certificate file not found at $CERT_FILE_PATH"
    continue
  fi

  # Extract the base name of the certificate file for the secret name
  CERT_BASE_NAME=$(basename "$CERT_FILE_PATH" .p12)
  SECRET_NAME="${SECRET_NAME_PREFIX}-${CERT_BASE_NAME}"

  # Base64-encode the certificate content
  ENCODED_CERT=$(base64 -w 0 "$CERT_FILE_PATH")

  # Construct the secret YAML in one line
  SECRET_YAML=$(echo -n "apiVersion: v1,kind: Secret,metadata: {name: $SECRET_NAME, namespace: $NAMESPACE},data: {cert.p12: $ENCODED_CERT}")

  # Output the one-line YAML to a file
  OUTPUT_FILE="secret-${CERT_BASE_NAME}.yaml"
  echo "$SECRET_YAML" > "$OUTPUT_FILE"
  echo "One-line secret YAML has been written to $OUTPUT_FILE"
done

# Optionally, apply all secrets to the cluster
# for CERT_FILE_PATH in "${CERT_FILES[@]}"; do
#   CERT_BASE_NAME=$(basename "$CERT_FILE_PATH" .p12)
#   OUTPUT_FILE="secret-${CERT_BASE_NAME}.yaml"
#   kubectl apply -f "$OUTPUT_FILE"
# done
----


{{- range $cert := ["cert1", "cert2", "cert3", "cert4", "cert5", "cert6", "cert7", "cert8", "cert9", "cert10"] }}
{{- with secret (printf "pki_int/issue/my-role" $cert) "common_name={{$cert}}.example.com" "ttl=720h" }}
{{- $certData := .Data }}
{{- $certName := $cert }}
{{- $certFile := (printf "/tmp/%s.pem" $certName) }}
{{- $keyFile := (printf "/tmp/%s-key.pem" $certName) }}
{{- $caFile := (printf "/tmp/%s-ca.pem" $certName) }}
{{- $p12File := (printf "/tmp/%s.p12" $certName) }}
{{- $p12Password := "yourpassword" }}

# Write the certificate, key, and CA to temporary files
{{- $certData.certificate | file $certFile }}
{{- $certData.private_key | file $keyFile }}
{{- $certData.issuing_ca | file $caFile }}

# Combine them into a .p12 file using openssl
{{- exec "openssl" "pkcs12" "-export" "-out" $p12File "-inkey" $keyFile "-in" $certFile "-certfile" $caFile "-password" (print "pass:" $p12Password) }}

# Base64-encode the .p12 file
{{- $encodedP12 := fileContent | base64Encode (cat $p12File) }}

apiVersion: v1
kind: Secret
metadata:
  name: my-tls-secret-{{ $certName }}
  namespace: default
data:
  cert.p12: {{ $encodedP12 }}
---
{{- end }}
{{- end }}
