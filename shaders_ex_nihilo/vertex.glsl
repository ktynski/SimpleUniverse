attribute vec3 aVertexPosition;
attribute vec3 aVertexNormal;
attribute vec3 aVertexColor;

uniform mat4 uModelViewMatrix;
uniform mat4 uProjectionMatrix;
uniform mat4 uNormalMatrix;

// Bootstrap parameters (emergent, not hardcoded)
uniform float uEvolutionProgress;
uniform float uGoldenRatio;
uniform float uPentagonAngle;

varying highp vec3 vLighting;
varying lowp vec3 vColor;
varying highp vec3 vPosition;
varying highp float vEvolutionFactor;

void main() {
    vec4 position = uModelViewMatrix * vec4(aVertexPosition, 1.0);

    // Apply evolution-based transformations
    float evolutionScale = 0.1 + uEvolutionProgress * 2.0;
    position.xyz *= evolutionScale;

    // Add golden ratio rotation based on evolution
    float rotationAngle = uEvolutionProgress * uGoldenRatio * 3.14159;
    float cosR = cos(rotationAngle);
    float sinR = sin(rotationAngle);

    // Rotate around Y axis using golden ratio
    float newX = position.x * cosR - position.z * sinR;
    float newZ = position.x * sinR + position.z * cosR;
    position.x = newX;
    position.z = newZ;

    gl_Position = uProjectionMatrix * position;

    // Lighting calculations
    vec3 ambientLight = vec3(0.3, 0.3, 0.3);
    vec3 directionalLightColor = vec3(1.0, 1.0, 1.0);
    vec3 directionalVector = normalize(vec3(0.85, 0.8, 0.75));

    vec3 transformedNormal = (uNormalMatrix * vec4(aVertexNormal, 1.0)).xyz;
    float directional = max(dot(transformedNormal, directionalVector), 0.0);

    vLighting = ambientLight + (directionalLightColor * directional);
    vColor = aVertexColor;
    vPosition = position.xyz;
    vEvolutionFactor = uEvolutionProgress;
}
