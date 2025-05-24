#!/usr/bin/env python3

import sys
import random

class FiniteField:
    """Finite field arithmetic operations"""
    
    @staticmethod
    def add(a, b, p):
        """Addition in finite field Zp"""
        return (a + b) % p
    
    @staticmethod
    def subtract(a, b, p):
        """Subtraction in finite field Zp"""
        return (a - b) % p
    
    @staticmethod
    def multiply(a, b, p):
        """Multiplication in finite field Zp"""
        return (a * b) % p
    
    @staticmethod
    def power(base, exp, p):
        """Exponentiation in finite field Zp using fast exponentiation"""
        result = 1
        base = base % p
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % p
            exp = exp >> 1
            base = (base * base) % p
        return result
    
    @staticmethod
    def inverse(a, p):
        """Multiplicative inverse in finite field Zp using extended Euclidean algorithm"""
        if a == 0:
            return 0
        
        # Extended Euclidean Algorithm
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % p, p)
        if gcd != 1:
            return 0  # No inverse exists
        return (x % p + p) % p
    
    @staticmethod
    def divide(a, b, p):
        """Division in finite field Zp (a / b = a * b^(-1))"""
        return FiniteField.multiply(a, FiniteField.inverse(b, p), p)

class EllipticCurve:
    """Elliptic curve operations for secp256k1 (y^2 = x^3 + 7)"""
    
    def __init__(self, p):
        self.p = p
        self.a = 0  # secp256k1 parameter
        self.b = 7  # secp256k1 parameter
        self.O = None  # Point at infinity
    
    def is_point_at_infinity(self, point):
        """Check if point is the point at infinity"""
        return point is None
    
    def point_add(self, P, Q):
        """Add two points on the elliptic curve"""
        # Handle point at infinity cases
        if self.is_point_at_infinity(P):
            return Q
        if self.is_point_at_infinity(Q):
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        # Check if points are inverses of each other
        if x1 == x2:
            if y1 == FiniteField.subtract(0, y2, self.p):
                return self.O  # Point at infinity
            elif y1 == y2:
                return self.point_double(P)
        
        # Different points case
        # m = (y2 - y1) / (x2 - x1)
        numerator = FiniteField.subtract(y2, y1, self.p)
        denominator = FiniteField.subtract(x2, x1, self.p)
        m = FiniteField.divide(numerator, denominator, self.p)
        
        # x3 = m^2 - x1 - x2
        x3 = FiniteField.subtract(
            FiniteField.subtract(FiniteField.multiply(m, m, self.p), x1, self.p),
            x2, self.p
        )
        
        # y3 = m(x1 - x3) - y1
        y3 = FiniteField.subtract(
            FiniteField.multiply(m, FiniteField.subtract(x1, x3, self.p), self.p),
            y1, self.p
        )
        
        return (x3, y3)
    
    def point_double(self, P):
        """Double a point on the elliptic curve (P + P)"""
        if self.is_point_at_infinity(P):
            return self.O
        
        x, y = P
        
        # Check if y = 0 (point is its own inverse)
        if y == 0:
            return self.O
        
        # m = (3x^2 + a) / (2y) = 3x^2 / (2y) since a = 0 for secp256k1
        numerator = FiniteField.multiply(3, FiniteField.multiply(x, x, self.p), self.p)
        denominator = FiniteField.multiply(2, y, self.p)
        m = FiniteField.divide(numerator, denominator, self.p)
        
        # x3 = m^2 - 2x
        x3 = FiniteField.subtract(
            FiniteField.multiply(m, m, self.p),
            FiniteField.multiply(2, x, self.p),
            self.p
        )
        
        # y3 = m(x - x3) - y
        y3 = FiniteField.subtract(
            FiniteField.multiply(m, FiniteField.subtract(x, x3, self.p), self.p),
            y, self.p
        )
        
        return (x3, y3)
    
    def scalar_multiply(self, k, P):
        """Multiply point P by scalar k using double-and-add algorithm"""
        if k == 0 or self.is_point_at_infinity(P):
            return self.O
        
        if k == 1:
            return P
        
        # Handle negative k
        if k < 0:
            k = -k
            x, y = P
            P = (x, FiniteField.subtract(0, y, self.p))  # Negate point
        
        # Double-and-add algorithm
        result = self.O
        addend = P
        
        while k > 0:
            if k & 1:  # If k is odd
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
            k >>= 1
        
        return result

class ECDSA:
    """ECDSA signature scheme implementation"""
    
    def __init__(self, p, o, G):
        self.p = p  # Prime modulus for the field
        self.o = o  # Order of the curve (number of points)
        self.G = G  # Base point
        self.curve = EllipticCurve(p)
    
    def generate_keypair(self):
        """Generate a random private/public key pair"""
        # Generate random private key d in range [1, o-1]
        d = random.randint(1, self.o - 1)
        
        # Compute public key Q = d * G
        Q = self.curve.scalar_multiply(d, self.G)
        
        return d, Q
    
    def sign(self, d, h):
        """Sign hash h with private key d"""
        while True:
            # Generate random k in range [1, o-1]
            k = random.randint(1, self.o - 1)
            
            # Compute R = k * G
            R = self.curve.scalar_multiply(k, self.G)
            if self.curve.is_point_at_infinity(R):
                continue
            
            r = R[0]  # x-coordinate of R
            if r == 0:
                continue
            
            # Compute k^(-1) mod o
            k_inv = FiniteField.inverse(k, self.o)
            if k_inv == 0:
                continue
            
            # Compute s = k^(-1) * (h + r * d) mod o
            s = FiniteField.multiply(
                k_inv,
                FiniteField.add(h, FiniteField.multiply(r, d, self.o), self.o),
                self.o
            )
            
            if s == 0:
                continue
            
            return r, s
    
    def verify(self, Q, r, s, h):
        """Verify signature (r,s) for hash h with public key Q"""
        # Check if r and s are in valid range
        if r <= 0 or r >= self.o or s <= 0 or s >= self.o:
            return False
        
        # Compute s^(-1) mod o
        s_inv = FiniteField.inverse(s, self.o)
        if s_inv == 0:
            return False
        
        # Compute u1 = h * s^(-1) mod o
        u1 = FiniteField.multiply(h, s_inv, self.o)
        
        # Compute u2 = r * s^(-1) mod o
        u2 = FiniteField.multiply(r, s_inv, self.o)
        
        # Compute R = u1 * G + u2 * Q
        point1 = self.curve.scalar_multiply(u1, self.G)
        point2 = self.curve.scalar_multiply(u2, Q)
        R = self.curve.point_add(point1, point2)
        
        if self.curve.is_point_at_infinity(R):
            return False
        
        # Check if x-coordinate of R equals r
        return R[0] == r

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ecdsa.py <mode> [parameters...]")
        return
    
    mode = sys.argv[1]
    
    if mode == "userid":
        # Replace with your actual user ID
        print("your_userid_here")
    
    elif mode == "genkey":
        if len(sys.argv) != 6:
            print("Usage: genkey p o Gx Gy")
            return
        
        p = int(sys.argv[2])
        o = int(sys.argv[3])
        Gx = int(sys.argv[4])
        Gy = int(sys.argv[5])
        G = (Gx, Gy)
        
        ecdsa = ECDSA(p, o, G)
        d, Q = ecdsa.generate_keypair()
        
        print(d)
        print(Q[0])
        print(Q[1])
    
    elif mode == "sign":
        if len(sys.argv) != 8:
            print("Usage: sign p o Gx Gy d h")
            return
        
        p = int(sys.argv[2])
        o = int(sys.argv[3])
        Gx = int(sys.argv[4])
        Gy = int(sys.argv[5])
        d = int(sys.argv[6])
        h = int(sys.argv[7])
        G = (Gx, Gy)
        
        ecdsa = ECDSA(p, o, G)
        r, s = ecdsa.sign(d, h)
        
        print(r)
        print(s)
    
    elif mode == "verify":
        if len(sys.argv) != 11:
            print("Usage: verify p o Gx Gy Qx Qy r s h")
            return
        
        p = int(sys.argv[2])
        o = int(sys.argv[3])
        Gx = int(sys.argv[4])
        Gy = int(sys.argv[5])
        Qx = int(sys.argv[6])
        Qy = int(sys.argv[7])
        r = int(sys.argv[8])
        s = int(sys.argv[9])
        h = int(sys.argv[10])
        
        G = (Gx, Gy)
        Q = (Qx, Qy)
        
        ecdsa = ECDSA(p, o, G)
        is_valid = ecdsa.verify(Q, r, s, h)
        
        print("True" if is_valid else "False")
    
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()