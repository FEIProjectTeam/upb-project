function convertArrayBufferToPem(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = window.btoa(binary);
    return `-----BEGIN PUBLIC KEY-----\n${base64}\n-----END PUBLIC KEY-----`;
}

function exportPublicKey(key) {
    return window.crypto.subtle.exportKey(
        "spki",
        key
    )
        .then(convertArrayBufferToPem)
        .catch(function (err) {
            console.error('Error exporting public key:', err);
        });
}

function base64ToArrayBuffer(base64) {
    var binary_string = window.atob(base64);
    var len = binary_string.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}

function importPrivateKey(pem) {
    // Replace headers and footers with empty strings and remove any newlines
    const pemContents = pem.replace(/(-----(BEGIN|END) PRIVATE KEY-----|\r\n|\n|\r)/g, '');

    // Base64 decode the string to get the binary data
    const binaryDer = base64ToArrayBuffer(pemContents);

    // Import the key into the crypto subsystem
    return window.crypto.subtle.importKey(
        "pkcs8", // Make sure this matches the format of your PEM
        binaryDer,
        {
            name: "RSA-OAEP",
            hash: "SHA-256",
        },
        true,
        ["decrypt"]
    ).then(cryptoKey => {
        console.log('Key imported successfully:', cryptoKey);
        return cryptoKey;
    }).catch(error => {
        console.error('Error importing key:', error);
    });
}

function decryptWithPrivateKey(encryptedDataBase64, privateKey) {
    const encryptedBuffer = base64ToArrayBuffer(encryptedDataBase64);
    return window.crypto.subtle.decrypt(
        {
            name: "RSA-OAEP"
        },
        privateKey, // This should be a CryptoKey object
        encryptedBuffer
    )
        .then(function (decryptedBuffer) {
            // returns an ArrayBuffer containing the decrypted data
            return new TextDecoder().decode(decryptedBuffer);
        })
        .catch(function (err) {
            console.error('Error decrypting data:', err);
            throw err; // Re-throw the error to be caught by the caller
        });
}

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
    formData.append('public_key', pem);

    fetch('/encrypt/pub-key/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: formData,
    })
        .catch((error) => {
            console.error('Error:', error);
        });
}

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
        .catch(function (err) {
            console.error('Error exporting private key:', err);
        });
}

