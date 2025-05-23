# ECDSA Implementation

A complete implementation of the Elliptic Curve Digital Signature Algorithm (ECDSA) using the secp256k1 curve parameters. This implementation includes finite field arithmetic, elliptic curve operations, and digital signature generation/verification.

## Overview

This project implements ECDSA from scratch without using external cryptographic libraries. It demonstrates:
- **Finite field arithmetic** operations in prime fields
- **Elliptic curve point operations** (addition, doubling, scalar multiplication)
- **Digital signature generation** using ECDSA
- **Signature verification** with public key cryptography
- **Key pair generation** for public/private key pairs

## Features

### 🔢 Finite Field Operations
- **Addition, subtraction, multiplication** in prime fields Zp
- **Modular exponentiation** using fast exponentiation
- **Multiplicative inverse** using extended Euclidean algorithm
- **Division** implemented as multiplication by inverse

### 📐 Elliptic Curve Operations
- **Point addition** for two different points on secp256k1
- **Point doubling** (adding a point to itself)
- **Scalar multiplication** using double-and-add algorithm (logarithmic time)
- **Point at infinity** handling for edge cases
- **secp256k1 curve** (y² = x³ + 7) implementation

### 🔐 ECDSA Implementation
- **Key generation** with random private key selection
- **Digital signature creation** with (r,s) format
- **Signature verification** using public key
- **Hash-based signing** (hash values provided as integers)

## Technical Details

### Curve Parameters
- **Curve equation**: y² = x³ + 7 (secp256k1)
- **Parameters**: a = 0, b = 7
- **Prime modulus**: p (field size)
- **Curve order**: o (number of points)
- **Base point**: G = (Gx, Gy)

### Algorithms Used
- **Extended Euclidean Algorithm** for modular inverses
- **Double-and-add method** for efficient scalar multiplication
- **Fast exponentiation** for modular exponentiation
- **ECDSA standard** for signature generation and verification

## Installation & Setup

### Prerequisites
- Python 3.x (no external libraries required)

### Setup Files
1. Save the main implementation as `ecdsa.py`
2. Create shell script `ecdsa.sh`:
   ```bash
   #!/bin/bash
   python3 ecdsa.py $@
   ```
3. Make executable:
   ```bash
   chmod 755 ecdsa.sh
   ```
4. Create `Makefile`:
   ```makefile
   main:
   	echo "ECDSA build complete"
   ```

## Usage Guide

### Command Modes

#### Get User ID
```bash
./ecdsa.sh userid
# Output: your_userid_here
```

#### Generate Key Pair
```bash
./ecdsa.sh genkey p o Gx Gy
# Example: ./ecdsa.sh genkey 43 31 25 25
# Output:
# 16    (private key d)
# 37    (public key Qx)
# 36    (public key Qy)
```

#### Sign Message
```bash
./ecdsa.sh sign p o Gx Gy d h
# Example: ./ecdsa.sh sign 43 31 25 25 16 30
# Output:
# 12    (signature r)
# 24    (signature s)
```

#### Verify Signature
```bash
./ecdsa.sh verify p o Gx Gy Qx Qy r s h
# Example: ./ecdsa.sh verify 43 31 25 25 37 36 12 24 30
# Output: True
```

### Parameter Explanation
- **p**: Prime modulus (field size)
- **o**: Curve order (number of points on curve)
- **Gx, Gy**: Base point coordinates
- **d**: Private key (random integer in [1, o-1])
- **Qx, Qy**: Public key coordinates (Q = d × G)
- **r, s**: Signature components
- **h**: Hash of message being signed (integer in [1, o-1])

## Example Walkthrough

Using the test parameters: p = 43, o = 31, G = (25,25)

### 1. Key Generation
```bash
./ecdsa.sh genkey 43 31 25 25
```
- Generates random private key d = 16
- Computes public key Q = 16 × (25,25) = (37,36)

### 2. Message Signing
```bash
./ecdsa.sh sign 43 31 25 25 16 30
```
- Uses private key d = 16 and hash h = 30
- Generates random k = 17
- Computes R = 17 × (25,25) = (12,12)
- Sets r = 12 (x-coordinate of R)
- Computes s = k⁻¹(h + r×d) mod o = 11×(30 + 12×16) mod 31 = 24
- Returns signature (r,s) = (12,24)

### 3. Signature Verification
```bash
./ecdsa.sh verify 43 31 25 25 37 36 12 24 30
```
- Uses public key Q = (37,36) and signature (12,24)
- Computes s⁻¹ = 24⁻¹ = 22 in Z₃₁
- Computes R = (s⁻¹×h)×G + (s⁻¹×r)×Q
- R = 9×(25,25) + 16×(37,36) = (2,31) + (29,31) = (12,12)
- Since x-coordinate (12) equals r, signature is valid

## Test Parameters

The implementation has been tested with various curve parameters:

```bash
# Small field for testing
p = 43, o = 31, G = (25,25)

# Medium fields
p = 79, o = 67, G = (35,8)
p = 127, o = 127, G = (93,33)

# Larger field
p = 733, o = 691, G = (336,170)
```

## Algorithm Complexity

- **Finite field operations**: O(log n) for exponentiation and inverse
- **Elliptic curve addition**: O(1)
- **Scalar multiplication**: O(log k) using double-and-add
- **Overall ECDSA**: O(log k) where k is the scalar multiplier

## Security Considerations

- **Random number generation**: Uses Python's random module (not cryptographically secure, but suitable for educational purposes)
- **Side-channel resistance**: Implementation focuses on correctness rather than timing attack prevention
- **Field validation**: Assumes all input parameters are valid and in correct ranges

## Corner Cases Handled

- **Point at infinity**: Proper handling of identity element in elliptic curve group
- **Point doubling**: Special case when adding a point to itself
- **Inverse points**: Adding a point and its reflection yields point at infinity
- **Zero values**: Regenerates random values if r or s equals zero during signing

## Verification Tools

Online calculators for verification:
- [Elliptic Curve Addition](https://andrea.corbellini.name/ecc/interactive/reals-add.html)
- [Elliptic Curve Multiplication](https://andrea.corbellini.name/ecc/interactive/reals-mul.html)

## File Structure

```
.
├── ecdsa.py          # Main implementation
├── ecdsa.sh          # Shell script wrapper
├── Makefile          # Build configuration
└── README.md         # This documentation
```

## Limitations

- **Field size**: Designed for small field sizes (≤ 1000) for educational purposes
- **Performance**: Optimized for correctness rather than speed
- **Random generation**: Uses standard random module, not cryptographically secure
- **Error handling**: Minimal error checking as per assignment requirements

## Mathematical Foundation

The implementation is based on:
- **Elliptic Curve Discrete Logarithm Problem** (ECDLP)
- **Finite field arithmetic** in prime fields
- **Group theory** for elliptic curve operations
- **Digital signature schemes** following ECDSA standard

## License

Educational implementation for cryptography coursework.