import { WorkstationMonitorState, WorkstationMonitorWorkerButtonState } from './WorkstationMonitor';
export enum WorkstationStatus {
  IDLE,
  IN_USE
}

export interface Sensor {
  id: number;
  name: string;
  active: boolean;
}

export interface SensorChangeEvent {
  sensor: Sensor;
  active: boolean;
}

export interface SensorChangeListener {
  (event: SensorChangeEvent): void;
}

export interface SensorSource {
  listSensors(): Sensor[];
  addSensorChangeListener(listener: SensorChangeListener): void;
}

export class DummySensorSource implements SensorSource {
  listSensors() {
    return [
      {id: 1, name: "Sensori 1", active: true},
      {id: 2, name: "Sensori 2", active: false}
    ];
  }

  addSensorChangeListener(listener: SensorChangeListener) {
  }
}

export interface WorkstationMonitorSensorCardState {
  id: number;
  name: string;
  active: boolean;
}

export interface WorkstationMonitorWorkerButtonState {
  numWorkers: number;
  active: boolean;
  onClick(): void;
}

export interface WorkstationMonitorState {
  sensorCardStates: WorkstationMonitorSensorCardState[];
  batchName: string;
  batchCardCode: string;
  onBatchCardCodeChanged(batchCardCode: string): void;
  workerButtonStates: WorkstationMonitorWorkerButtonState[];
  workstationStatus: WorkstationStatus;
}

export interface WorkstationMonitorStateChangeListener {
  (newState: Partial<WorkstationMonitorState>): void;
}

export class WorkstationMonitor {
  private _sensorSource: SensorSource;
  private _stateChangeListeners: WorkstationMonitorStateChangeListener[];
  private _state: WorkstationMonitorState;
  private _numWorkers: number;
  private _maxWorkers: number;

  constructor(sensorSource: SensorSource) {
    console.log(sensorSource);
    this._sensorSource = sensorSource;
    this._stateChangeListeners = [];
    this._numWorkers = 0;
    this._maxWorkers = 5;
    this._state = {
      sensorCardStates: this._sensorSource.listSensors(),
      batchName: "",
      batchCardCode: "",
      workerButtonStates: this.createWorkerButtonStates(),
      onBatchCardCodeChanged: (code) => this.onBatchCardCodeChanged(code),
      workstationStatus: WorkstationStatus.IDLE
    };
  }

  private updateState(stateChange: Partial<WorkstationMonitorState>) {
    Object.assign(this._state, stateChange);
    for (const listener of this._stateChangeListeners) {
      listener(stateChange);
    }
  }

  private createWorkerButtonStates(): WorkstationMonitorWorkerButtonState[] {
    var buttons = [];
    for (let i=0; i<this._maxWorkers; i++) {
      buttons.push({
        numWorkers: i,
        active: i == this._numWorkers,
        onClick: () => {
          console.log(`numWorkers = ${i}`);
          this._numWorkers = i;
          this.updateState({workerButtonStates: this.createWorkerButtonStates()});
        }
      });
    }
    return buttons;
  }

  init(): void {
    this._sensorSource.addSensorChangeListener((event) => {
    });
  }

  onBatchCardCodeChanged(batchCardCode: string): boolean {
    this.updateState({batchCardCode});
    return true;
  }

  addStateChangeListener(listener: WorkstationMonitorStateChangeListener) {
    this._stateChangeListeners.push(listener);
  }

  get state(): WorkstationMonitorState {
    return this._state;
  }

}