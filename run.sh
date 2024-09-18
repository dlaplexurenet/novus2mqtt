#!/usr/bin/env bash
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

if [ -z "${MQTT_BROKER}" ]; then
    echo "Missing required environment variable: MQTT_BROKER"
    exit 1
fi

if [ -z "${MQTT_BASE_PREFIX}" ] && [ "${HASS_DISCOVERY}" != "true" ]; then
    echo "Missing required environment variable: either MQTT_BASE_PREFIX or HASS_DISCOVERY"
    exit 1
fi

PARAMS=(--mqtt-broker="${MQTT_BROKER}" --mqtt-base-prefix="${MQTT_BASE_PREFIX}")

if [ -n "${LOG_LEVEL}" ]; then
    PARAMS+=(--log-level="${LOG_LEVEL}")
fi

if [ -n "${MQTT_PORT}" ]; then
    PARAMS+=(--mqtt-port="${MQTT_PORT}")
fi

if [ -n "${MQTT_USERNAME}" ]; then
    PARAMS+=(--mqtt-username="${MQTT_USERNAME}")
fi

if [ -n "${MQTT_PASSWORD}" ]; then
    PARAMS+=(--mqtt-password="${MQTT_PASSWORD}")
fi

if [ "${HASS_DISCOVERY}" = "true" ]; then
    PARAMS+=(--hass-discovery)
fi

if [ -n "${HASS_DISCOVERY_PREFIX}" ]; then
    PARAMS+=(--hass-discovery-prefix="${HASS_DISCOVERY_PREFIX}")
fi

if [ -n "${NOVUS_CONFIG}" ]; then
    PARAMS+=(--novus-config="${NOVUS_CONFIG}")
fi

python3 main.py "${PARAMS[@]}"
