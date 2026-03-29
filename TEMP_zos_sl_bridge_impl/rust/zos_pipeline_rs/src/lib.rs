use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResonanceScore {
    pub hash_u64: u64,
    pub o71: u64,
    pub o59: u64,
    pub o47: u64,
    pub dist_primary: u64,
    pub dist_secondary: u64,
    pub resonance_strength: f64,
    pub resonance: bool,
}

pub fn hash_file_bytes(data: &[u8]) -> u64 {
    let digest = Sha256::digest(data);
    let mut buf = [0u8; 8];
    buf.copy_from_slice(&digest[..8]);
    u64::from_be_bytes(buf)
}

pub fn orbifold_coords(h: u64) -> (u64, u64, u64) {
    (h % 71, h % 59, h % 47)
}

fn mod_dist(lhs: u64, rhs: u64, modulus: u64) -> u64 {
    let d = lhs.abs_diff(rhs) % modulus;
    d.min(modulus - d)
}

pub fn resonance_score_from_hash(h: u64, threshold: u64) -> ResonanceScore {
    let (o71, o59, o47) = orbifold_coords(h);
    let dist_primary = mod_dist(o59, (o71 + 24) % 59, 59);
    let dist_secondary = mod_dist(o59, o71 % 59, 59);
    let best = dist_primary.min(dist_secondary);
    let strength = (1.0 - (best as f64 / threshold.max(1) as f64)).max(0.0);

    ResonanceScore {
        hash_u64: h,
        o71,
        o59,
        o47,
        dist_primary,
        dist_secondary,
        resonance_strength: strength,
        resonance: best < threshold,
    }
}

pub fn resonance_score(data: &[u8], threshold: u64) -> ResonanceScore {
    resonance_score_from_hash(hash_file_bytes(data), threshold)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn smoke() {
        let s = resonance_score(b"tenant mould", 3);
        assert!(s.o71 < 71);
        assert!(s.o59 < 59);
        assert!(s.o47 < 47);
    }
}
