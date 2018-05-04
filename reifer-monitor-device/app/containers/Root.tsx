import * as React from 'react';
import { WorkstationMonitor,
         WorkstationMonitorState, 
         DummySensorSource} from '../model/WorkstationMonitor';

const styles = require('./Root.scss');

export default class Root extends React.Component<{}, WorkstationMonitorState> {
  private _workstationMonitor: WorkstationMonitor;

  constructor(props: {}) {
    super(props);

    this._workstationMonitor = new WorkstationMonitor(
      new DummySensorSource()
    );

    console.log(this._workstationMonitor);

    this.state = this._workstationMonitor.state;
    this._workstationMonitor.addStateChangeListener((state) => {
      this.setState(this._workstationMonitor.state);
    });
  }

  render() {
    return (
    <div className={styles.container}>
      <div className={styles.uiContainer}>
        <div className={styles.controlGroupLabel}>
          Anturien tila
        </div>
        {this.state.sensorCardStates.length === 0 ? <div/> : null}
        {this.state.sensorCardStates.map((card) => 
          <div className={card.active ? styles.sensorStatusCardActive
                                      : styles.sensorStatusCardInactive}
               key={String(card.id)}>
            <div>{card.name}</div>
            <div className={styles.sensorStatus}>
              {card.active ? "AKTIIVINEN" : "EI AKTIIVINEN"}
            </div>
          </div>
        )}
        <div className={styles.controlGroupLabel}>
          Tuotantoerä
        </div>
        <div className={styles.orderNameLabel}>{this.state.batchName}</div>
        <input type="text"
               value={this.state.batchCardCode}
               className={styles.orderCodeField}
               onChange={(ev) => {
                 this.state.onBatchCardCodeChanged(ev.currentTarget.value);
               } } />
        <div className={styles.controlGroupLabel}>
          Työntekijöiden lukumäärä
        </div>
        {this.state.workerButtonStates.length === 0 ? <div/> : null}
        {this.state.workerButtonStates.map((worker, i) =>
          <button
            key={`${i}`}
            onClick={worker.onClick}
            className={worker.active ? styles.numEmployeesButtonSelected
                                     : styles.numEmployeesButton}>
            <div>{worker.numWorkers}</div>
          </button>
        )}
      </div>
      <div className={styles.workstationStatusCard}>
          <div>Työpisteen tila</div>
          <div><b>{this.state.workstationStatus}</b></div>
        </div>
      </div>
    );
  }
}