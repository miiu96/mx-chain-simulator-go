package facade

import (
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"strconv"
	"strings"

	"github.com/multiversx/mx-chain-core-go/core/check"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	dtoc "github.com/multiversx/mx-chain-simulator-go/pkg/dtos"
)

const errMsgAccountNotFound = "account was not found"

type simulatorFacade struct {
	simulator SimulatorHandler
}

// NewSimulatorFacade will create a new instance of simulatorFacade
func NewSimulatorFacade(simulator SimulatorHandler) (*simulatorFacade, error) {
	if check.IfNil(simulator) {
		return nil, errNilSimulatorHandler
	}

	return &simulatorFacade{
		simulator: simulator,
	}, nil
}

// GenerateBlocks will generate a provided number of blocks
func (sf *simulatorFacade) GenerateBlocks(numOfBlocks int) error {
	if numOfBlocks <= 0 {
		return errInvalidNumOfBlocks
	}
	return sf.simulator.GenerateBlocks(numOfBlocks)
}

// GetInitialWalletKeys will return the initial wallets
func (sf *simulatorFacade) GetInitialWalletKeys() *dtos.InitialWalletKeys {
	return sf.simulator.GetInitialWalletKeys()
}

// SetKeyValueForAddress will set the provided state for an address
func (sf *simulatorFacade) SetKeyValueForAddress(address string, keyValueMap map[string]string) error {
	return sf.simulator.SetKeyValueForAddress(address, keyValueMap)
}

// SetStateMultiple will set the entire state for the provided addresses
func (sf *simulatorFacade) SetStateMultiple(stateSlice []*dtos.AddressState) error {
	return sf.simulator.SetStateMultiple(stateSlice)
}

// SetStateMultipleOverwrite will set the entire state for the provided address and cleanup the old state of the provided addresses
func (sf *simulatorFacade) SetStateMultipleOverwrite(stateSlice []*dtos.AddressState) error {
	for _, state := range stateSlice {
		// TODO MX-15414
		err := sf.simulator.RemoveAccounts([]string{state.Address})
		shouldReturnErr := err != nil && !strings.Contains(err.Error(), errMsgAccountNotFound)
		if shouldReturnErr {
			return err
		}
	}

	return sf.simulator.SetStateMultiple(stateSlice)
}

// AddValidatorKeys will add the validator keys in the multi key handler
func (sf *simulatorFacade) AddValidatorKeys(validators *dtoc.ValidatorKeys) error {
	validatorsPrivateKeys := make([][]byte, 0, len(validators.PrivateKeysBase64))
	for idx, privateKeyBase64 := range validators.PrivateKeysBase64 {
		privateKeyHexBytes, err := base64.StdEncoding.DecodeString(privateKeyBase64)
		if err != nil {
			return fmt.Errorf("cannot base64 decode key index=%d, error=%s", idx, err.Error())
		}

		privateKeyBytes, err := hex.DecodeString(string(privateKeyHexBytes))
		if err != nil {
			return fmt.Errorf("cannot hex decode key index=%d, error=%s", idx, err.Error())
		}

		validatorsPrivateKeys = append(validatorsPrivateKeys, privateKeyBytes)
	}

	return sf.simulator.AddValidatorKeys(validatorsPrivateKeys)
}

// GenerateBlocksUntilEpochIsReached will generate as many blocks are required until the target epoch is reached
func (sf *simulatorFacade) GenerateBlocksUntilEpochIsReached(targetEpoch int32) error {
	return sf.simulator.GenerateBlocksUntilEpochIsReached(targetEpoch)
}

// ForceUpdateValidatorStatistics will force the reset of the cache used for the validators statistics endpoint
func (sf *simulatorFacade) ForceUpdateValidatorStatistics() error {
	return sf.simulator.ForceResetValidatorStatisticsCache()
}

// GetObserversInfo will return information about the observers
func (sf *simulatorFacade) GetObserversInfo() (map[uint32]*dtoc.ObserverInfo, error) {
	restApiInterface := sf.simulator.GetRestAPIInterfaces()

	response := make(map[uint32]*dtoc.ObserverInfo)
	for shardID, apiInterface := range restApiInterface {
		split := strings.Split(apiInterface, ":")
		if len(split) != 2 {
			return nil, fmt.Errorf("cannot extract port for shard ID=%d", shardID)
		}

		port, err := strconv.Atoi(split[1])
		if err != nil {
			return nil, fmt.Errorf("cannot cast port string to int for shard ID=%d", shardID)
		}

		response[shardID] = &dtoc.ObserverInfo{
			APIPort: port,
		}
	}

	return response, nil
}

// IsInterfaceNil returns true if there is no value under the interface
func (sf *simulatorFacade) IsInterfaceNil() bool {
	return sf == nil
}
