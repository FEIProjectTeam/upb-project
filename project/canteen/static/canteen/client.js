// Function to convert an ArrayBuffer to PEM format string
function convertArrayBufferToPem(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = window.btoa(binary);
    return `-----BEGIN PUBLIC KEY-----\n${base64}\n-----END PUBLIC KEY-----`;
}

// Function to convert a hex string to an ArrayBuffer
function hexStringToArrayBuffer(hexString) {
    if (hexString.length % 2 !== 0) {
        throw "HexString needs to be in even length";
    }
    var arrayBuffer = new Uint8Array(hexString.length / 2);
    for (var i = 0; i < hexString.length; i += 2) {
        var byteValue = parseInt(hexString.substr(i, 2), 16);
        arrayBuffer[i / 2] = byteValue;
    }
    return arrayBuffer.buffer;
}

// Function to export the public key in PEM format
function exportPublicKey(key) {
    return window.crypto.subtle.exportKey(
        "spki",
        key
    )
    .then(convertArrayBufferToPem)
    .catch(function(err){
        console.error('Error exporting public key:', err);
    });
}

function importPrivateKey(pem) {
    // Fetch the part of the PEM string between header and footer
    const pemHeader = "-----BEGIN PRIVATE KEY-----";
    const pemFooter = "-----END PRIVATE KEY-----";
    const pemContents = pem.substring(pemHeader.length, pem.length - pemFooter.length);
    // Base64 decode the string to get the binary data
    const binaryDerString = window.atob(pemContents);
    // Convert from a binary string to an ArrayBuffer
    const binaryDer = str2ab(binaryDerString);

    return window.crypto.subtle.importKey(
        "pkcs8",
        binaryDer,
        {
            name: "RSA-OAEP",
            hash: "SHA-256",
        },
        true,
        ["decrypt"]
    );
}

function str2ab(str) {
    const buffer = new ArrayBuffer(str.length);
    const bufferView = new Uint8Array(buffer);
    for (let i=0; i < str.length; i++) {
        bufferView[i] = str.charCodeAt(i);
    }
    return buffer;
}

// Function to decrypt data with the private key
function decryptWithPrivateKey(encryptedDataBase64, privateKey) {
    const encryptedBuffer = base64ToArrayBuffer(encryptedDataBase64);
    return window.crypto.subtle.decrypt(
        {
            name: "RSA-OAEP"
        },
        privateKey, // This should be a CryptoKey object
        encryptedBuffer
    )
    .then(function(decryptedBuffer){
        // returns an ArrayBuffer containing the decrypted data
        return new TextDecoder().decode(decryptedBuffer);
    })
    .catch(function(err){
        console.error('Error decrypting data:', err);
        throw err; // Re-throw the error to be caught by the caller
    });
}

// Function to convert base64 encoded data to ArrayBuffer
function base64ToArrayBuffer(base64) {
    const binary_string = window.atob(base64);
    let len = binary_string.length;
    let bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++)        {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}

/* // Function to send the exported public key to the server
function sendPublicKeyToServer(pem) {
    fetch('/encrypt/pub-key/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ public_key: pem }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Public key sent to server:', data);
        // Assuming server sends back the encrypted data immediately
        if(data.encryptedData) {
            return decryptWithPrivateKey(data.encryptedData);
        }
        throw new Error('Encrypted data not received');
    })
    .then(decryptedData => {
        console.log('Decrypted data:', decryptedData);
        // Display or process the decrypted data here
    })
    .catch((error) => {
        console.error('Error:', error);
    });
} */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function sendPublicKeyToServer(pem) {
    const formData = new FormData();
    formData.append('public_key', pem); // Make sure 'public_key' is the correct field name for the form

    fetch('/encrypt/pub-key/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken, // Include the CSRF token
        },
        body: formData, // Send as FormData instead of JSON
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


// Function to generate key pair, export the public key, and send it to the server
function generateAndExportKey() {
    window.crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
            hash: {name: "SHA-256"},
        },
        true,
        ["encrypt", "decrypt"]
    )
    .then(function(keyPair){
        // Expose the private key to the window object (not recommended for production!)
        window.privateKey = keyPair.privateKey;
        return exportPublicKey(keyPair.publicKey);
    })
    .then(sendPublicKeyToServer)
    .catch(function(err){
        console.error('Error generating or exporting key:', err);
    });
}

// Start the key generation and export process
//generateAndExportKey();

// Function to convert an ArrayBuffer to PEM format string for a private key
function convertArrayBufferToPrivatePem(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = window.btoa(binary);
    return `-----BEGIN PRIVATE KEY-----\n${base64}\n-----END PRIVATE KEY-----`;
}

// Function to export the private key in PKCS#8 PEM format
function exportPrivateKey(privateKey) {
    return window.crypto.subtle.exportKey(
        "pkcs8",
        privateKey
    )
    .then(convertArrayBufferToPrivatePem)
    .catch(function(err){
        console.error('Error exporting private key:', err);
    });
}

