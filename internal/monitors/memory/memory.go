package memory

import (
	"context"
	"runtime"
	"time"

	"github.com/shirou/gopsutil/mem"
	"github.com/signalfx/golib/datapoint"
	"github.com/signalfx/signalfx-agent/internal/core/config"
	"github.com/signalfx/signalfx-agent/internal/monitors"
	"github.com/signalfx/signalfx-agent/internal/monitors/types"
	"github.com/signalfx/signalfx-agent/internal/utils"
	"github.com/sirupsen/logrus"
	log "github.com/sirupsen/logrus"
)

const monitorType = "memory"
const windowsOS = "windows"

func init() {
	monitors.Register(&monitorMetadata, func() interface{} { return &Monitor{} }, &Config{})
}

// Config for this monitor
type Config struct {
	config.MonitorConfig `singleInstance:"true" acceptsEndpoints:"false"`
}

// Monitor for Utilization
type Monitor struct {
	Output types.Output
	cancel func()
	logger logrus.FieldLogger
}

func (m *Monitor) processDatapointsWindows(memInfo *mem.VirtualMemoryStat, dimensions map[string]string) {
	m.Output.SendDatapoint(datapoint.New("memory.available", dimensions, datapoint.NewIntValue(int64(memInfo.Available)), datapoint.Gauge, time.Time{}))
}

func (m *Monitor) processDatapointsNotWindows(memInfo *mem.VirtualMemoryStat, dimensions map[string]string) {
	m.Output.SendDatapoint(datapoint.New("memory.free", dimensions, datapoint.NewIntValue(int64(memInfo.Free)), datapoint.Gauge, time.Time{}))
}

func (m *Monitor) processDatapointsDarwin(memInfo *mem.VirtualMemoryStat, dimensions map[string]string) {
	m.Output.SendDatapoint(datapoint.New("memory.active", dimensions, datapoint.NewIntValue(int64(memInfo.Active)), datapoint.Gauge, time.Time{}))
	m.Output.SendDatapoint(datapoint.New("memory.inactive", dimensions, datapoint.NewIntValue(int64(memInfo.Inactive)), datapoint.Gauge, time.Time{}))
	m.Output.SendDatapoint(datapoint.New("memory.wired", dimensions, datapoint.NewIntValue(int64(memInfo.Wired)), datapoint.Gauge, time.Time{}))
}

func (m *Monitor) processDatapointsLinux(memInfo *mem.VirtualMemoryStat, dimensions map[string]string) {
	m.Output.SendDatapoint(datapoint.New("memory.buffered", dimensions, datapoint.NewIntValue(int64(memInfo.Buffers)), datapoint.Gauge, time.Time{}))
	// for some reason gopsutil decided to add slab_reclaimable to cached which collectd does not
	m.Output.SendDatapoint(datapoint.New("memory.cached", dimensions, datapoint.NewIntValue(int64(memInfo.Cached-memInfo.SReclaimable)), datapoint.Gauge, time.Time{}))
	m.Output.SendDatapoint(datapoint.New("memory.slab_recl", dimensions, datapoint.NewIntValue(int64(memInfo.SReclaimable)), datapoint.Gauge, time.Time{}))
	m.Output.SendDatapoint(datapoint.New("memory.slab_unrecl", dimensions, datapoint.NewIntValue(int64(memInfo.Slab-memInfo.SReclaimable)), datapoint.Gauge, time.Time{}))
}

// EmitDatapoints emits a set of memory datapoints
func (m *Monitor) emitDatapoints() {
	// mem.VirtualMemory is a gopsutil function
	memInfo, err := mem.VirtualMemory()
	if err != nil {
		if err == context.DeadlineExceeded {
			m.logger.WithField("debug", err).Debugf("unable to collect memory time info")
		} else {
			m.logger.WithError(err).Errorf("unable to collect memory time info")
		}
		return
	}

	dimensions := map[string]string{"plugin": monitorType}

	// all platforms
	m.Output.SendDatapoint(datapoint.New("memory.utilization", map[string]string{"plugin": types.UtilizationMetricPluginName}, datapoint.NewFloatValue(memInfo.UsedPercent), datapoint.Gauge, time.Time{}))
	m.Output.SendDatapoint(datapoint.New("memory.used", dimensions, datapoint.NewIntValue(int64(memInfo.Used)), datapoint.Gauge, time.Time{}))

	// windows only
	if runtime.GOOS == windowsOS {
		m.processDatapointsWindows(memInfo, dimensions)
	}

	// linux + darwin only
	if runtime.GOOS != windowsOS {
		m.processDatapointsNotWindows(memInfo, dimensions)
	}

	// darwin only
	if runtime.GOOS == "darwin" {
		m.processDatapointsDarwin(memInfo, dimensions)
	}

	// linux only
	if runtime.GOOS == "linux" {
		m.processDatapointsLinux(memInfo, dimensions)
	}
}

// Configure is the main function of the monitor, it will report host metadata
// on a varied interval
func (m *Monitor) Configure(conf *Config) error {
	m.logger = logrus.WithFields(log.Fields{"monitorType": monitorType})
	if runtime.GOOS != windowsOS {
		m.logger.Warningf("'%s' monitor is in beta on this platform.  For production environments please use 'collectd/%s'.", monitorType, monitorType)
	}

	// create contexts for managing the the plugin loop
	var ctx context.Context
	ctx, m.cancel = context.WithCancel(context.Background())

	// gather metrics on the specified interval
	utils.RunOnInterval(ctx, func() {
		m.emitDatapoints()
	}, time.Duration(conf.IntervalSeconds)*time.Second)

	return nil
}

// Shutdown stops the metric sync
func (m *Monitor) Shutdown() {
	if m.cancel != nil {
		m.cancel()
	}
}
