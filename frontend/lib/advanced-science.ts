export const NIST_CONSTANTS = {
  rKcalMolK: 0.00198720425864083,
  hartreeToKcalMol: 627.509474,
  hartreeToEv: 27.211386245988,
  evToKcalMol: 23.060549286,
  kB: 1.380649e-23,
  h: 6.62607015e-34,
  defaultTemperatureK: 350
};

export function clamp(value: number, min = -50, max = 50) {
  return Math.max(min, Math.min(max, value));
}

export function calculateEyringRate(deltaGActKcalMol: number, temperatureK = NIST_CONSTANTS.defaultTemperatureK) {
  const prefactor = (NIST_CONSTANTS.kB * Math.max(temperatureK, 1e-12)) / NIST_CONSTANTS.h;
  const exponent = -deltaGActKcalMol / (NIST_CONSTANTS.rKcalMolK * Math.max(temperatureK, 1e-12));
  return prefactor * Math.exp(clamp(exponent));
}

export function calculateSelectivity(deltaGMajorKcalMol: number, deltaGMinorKcalMol: number, temperatureK = NIST_CONSTANTS.defaultTemperatureK) {
  const ddg = deltaGMinorKcalMol - deltaGMajorKcalMol;
  const ratio = Math.exp(clamp(ddg / (NIST_CONSTANTS.rKcalMolK * Math.max(temperatureK, 1e-12))));
  return (ratio / (1 + ratio)) * 100;
}

class Cholesky {
  L: number[][];
  constructor(A: number[][]) {
    const n = A.length;
    this.L = Array.from({ length: n }, () => new Array(n).fill(0));
    for (let i = 0; i < n; i++) {
      for (let j = 0; j <= i; j++) {
        let sum = 0;
        for (let k = 0; k < j; k++) {
          sum += this.L[i][k] * this.L[j][k];
        }
        if (i === j) {
          this.L[i][j] = Math.sqrt(Math.max(A[i][i] - sum, 1e-12));
        } else {
          this.L[i][j] = (A[i][j] - sum) / Math.max(Math.abs(this.L[j][j]), 1e-12);
        }
      }
    }
  }

  solve(b: number[]): number[] {
    const n = this.L.length;
    const y = new Array(n).fill(0);
    for (let i = 0; i < n; i++) {
      let sum = 0;
      for (let j = 0; j < i; j++) {
        sum += this.L[i][j] * y[j];
      }
      y[i] = (b[i] - sum) / Math.max(Math.abs(this.L[i][i]), 1e-12);
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) {
      let sum = 0;
      for (let j = i + 1; j < n; j++) {
        sum += this.L[j][i] * x[j];
      }
      x[i] = (y[i] - sum) / Math.max(Math.abs(this.L[i][i]), 1e-12);
    }
    return x;
  }
}

export class AdvancedGpr {
  private trainX: number[][] = [];
  private trainY: number[] = [];
  private alpha: number[] = [];
  private cholesky: Cholesky | null = null;

  constructor(
    private readonly lengthScale = 1,
    private readonly noiseVariance = 1e-6
  ) {}

  train(points: number[][], values: number[]) {
    this.trainX = points;
    this.trainY = values;
    const n = points.length;
    const K = Array.from({ length: n }, () => new Array(n).fill(0));
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        K[i][j] = this.kernel(points[i], points[j]) + (i === j ? this.noiseVariance : 0);
      }
    }
    this.cholesky = new Cholesky(K);
    this.alpha = this.cholesky.solve(values);
  }

  predict(point: number[]) {
    if (this.trainX.length === 0 || !this.cholesky) return { mean: 0, variance: 1 };
    const n = this.trainX.length;
    const kStar = new Array(n).fill(0);
    let mean = 0;
    for (let i = 0; i < n; i++) {
      kStar[i] = this.kernel(this.trainX[i], point);
      mean += this.alpha[i] * kStar[i];
    }
    const kSelf = this.kernel(point, point);
    const v = new Array(n).fill(0);
    for (let i = 0; i < n; i++) {
      let sum = 0;
      for (let j = 0; j < i; j++) {
        sum += this.cholesky.L[i][j] * v[j];
      }
      v[i] = (kStar[i] - sum) / Math.max(Math.abs(this.cholesky.L[i][i]), 1e-12);
    }
    let vTv = 0;
    for (let i = 0; i < n; i++) {
      vTv += v[i] * v[i];
    }
    const variance = kSelf - vTv;
    return { mean, variance: Math.max(variance, 1e-8) };
  }

  expectedImprovement(point: number[], bestValue: number, xi = 0.01) {
    const { mean, variance } = this.predict(point);
    const std = Math.sqrt(Math.max(variance, 0));
    if (std <= 1e-12) return 0;
    const z = (mean - bestValue - xi) / std;
    return Math.max(0, (mean - bestValue - xi) * normalCdf(z) + std * normalPdf(z));
  }

  private kernel(a: number[], b: number[]) {
    const distanceSq = a.reduce((sum, value, index) => sum + (value - (b[index] ?? 0)) ** 2, 0);
    return Math.exp(clamp(-distanceSq / Math.max(2 * this.lengthScale ** 2, 1e-12)));
  }
}

export class VmcPreviewEngine {
  private coords: number[][];
  private accepted = 0;
  private total = 0;

  constructor(
    electronCount: number,
    private stepSize = 0.5
  ) {
    this.coords = Array.from({ length: electronCount }, () => [Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5]);
  }

  run(steps = 300) {
    const energies: number[] = [];
    for (let index = 0; index < steps; index += 1) {
      this.metropolisStep();
      energies.push(this.estimateEnergy());
      if ((index + 1) % 50 === 0) this.tuneStepSize();
    }
    const block = blockAverage(energies, 25);
    return {
      meanEnergyHartree: block.mean,
      stdErrorHartree: block.stdError,
      acceptanceRatio: this.total ? this.accepted / this.total : 0,
      samples: steps,
      note: "VMC 为轻量示例采样，用于显示统计工作流，不代表真实电子相关能。"
    };
  }

  private metropolisStep() {
    this.total += 1;
    const proposal = this.coords.map((coord) => coord.map((value) => value + (Math.random() - 0.5) * this.stepSize));
    const logAlpha = this.logDensity(proposal) - this.logDensity(this.coords);
    if (Math.log(Math.random() + 1e-15) < logAlpha) {
      this.coords = proposal;
      this.accepted += 1;
    }
  }

  private logDensity(coords: number[][]) {
    let logD = 0;
    for (const coord of coords) {
      const radius = Math.sqrt(Math.max(coord[0] ** 2 + coord[1] ** 2 + coord[2] ** 2, 0));
      logD += -2 * radius;
    }
    for (let i = 0; i < coords.length; i += 1) {
      for (let j = i + 1; j < coords.length; j += 1) {
        const dx = coords[i][0] - coords[j][0];
        const dy = coords[i][1] - coords[j][1];
        const dz = coords[i][2] - coords[j][2];
        const rij = Math.sqrt(Math.max(dx * dx + dy * dy + dz * dz, 0));
        logD += (0.5 * rij) / Math.max(1 + rij, 1e-12);
      }
    }
    return logD;
  }

  private estimateEnergy() {
    return -78.4 + (Math.random() - 0.5) * 0.1;
  }

  private tuneStepSize() {
    const ratio = this.total ? this.accepted / this.total : 0;
    if (ratio > 0.55) this.stepSize *= 1.08;
    if (ratio < 0.45) this.stepSize *= 0.92;
    this.stepSize = Math.max(0.02, Math.min(this.stepSize, 4));
  }
}

export function runTsGuidanceExample() {
  const model = new AdvancedGpr(1.4, 1e-5);
  const trainingX = [
    [8.0, 0.8],
    [10.5, 0.4],
    [13.0, 1.1],
    [16.0, 1.8]
  ];
  const trainingY = [18.5, 15.2, 11.7, 7.1];
  model.train(trainingX, trainingY);
  const candidates = [
    { label: "MCSOMe-1,2-re", x: [11.2, 0.6] },
    { label: "MCSOMe-1,2-si", x: [12.4, 0.9] },
    { label: "DMOS-folded", x: [15.2, 1.7] },
    { label: "DCS-baseline", x: [9.3, 0.5] }
  ];
  const best = Math.max(...trainingY);
  return candidates
    .map((candidate) => {
      const prediction = model.predict(candidate.x);
      return {
        label: candidate.label,
        predictedScore: prediction.mean,
        uncertainty: Math.sqrt(prediction.variance),
        expectedImprovement: model.expectedImprovement(candidate.x, best)
      };
    })
    .sort((a, b) => b.expectedImprovement - a.expectedImprovement);
}

export function runVmcPreview() {
  return new VmcPreviewEngine(6).run(260);
}

function blockAverage(values: number[], blockSize: number) {
  if (values.length === 0) return { mean: 0, stdError: 0 };
  if (values.length < blockSize) {
    const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
    return { mean, stdError: 0 };
  }
  const blockCount = Math.floor(values.length / blockSize);
  const means = Array.from({ length: blockCount }, (_, blockIndex) => {
    const block = values.slice(blockIndex * blockSize, (blockIndex + 1) * blockSize);
    return block.reduce((sum, value) => sum + value, 0) / block.length;
  });
  const mean = means.reduce((sum, value) => sum + value, 0) / Math.max(means.length, 1e-12);
  const variance = means.reduce((sum, value) => sum + (value - mean) ** 2, 0) / Math.max(means.length - 1, 1e-12);
  return { mean, stdError: Math.sqrt(Math.max(variance / Math.max(means.length, 1e-12), 0)) };
}

function normalPdf(value: number) {
  return Math.exp(clamp(-0.5 * value * value)) / Math.sqrt(Math.max(2 * Math.PI, 0));
}

function normalCdf(value: number) {
  return 0.5 * (1 + Math.sign(value) * Math.sqrt(Math.max(1 - Math.exp(clamp((-2 * value * value) / Math.max(Math.PI, 1e-12))), 0)));
}
