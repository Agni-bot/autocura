package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// RollbackSpec define o estado desejado do Rollback
type RollbackSpec struct {
	// TargetVersion é a versão para a qual o rollback deve ser realizado
	TargetVersion string `json:"targetVersion"`

	// ResourceName é o nome do recurso que deve ser revertido
	ResourceName string `json:"resourceName"`

	// ResourceNamespace é o namespace do recurso
	ResourceNamespace string `json:"resourceNamespace"`

	// ResourceKind é o tipo do recurso (Deployment, StatefulSet, etc)
	ResourceKind string `json:"resourceKind"`
}

// RollbackStatus define o estado observado do Rollback
type RollbackStatus struct {
	// Phase representa a fase atual do rollback
	Phase string `json:"phase,omitempty"`

	// LastUpdateTime é o timestamp da última atualização
	LastUpdateTime metav1.Time `json:"lastUpdateTime,omitempty"`

	// Message contém informações sobre o estado atual
	Message string `json:"message,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// Rollback é o Schema para a API rollback
type Rollback struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   RollbackSpec   `json:"spec,omitempty"`
	Status RollbackStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// RollbackList contém uma lista de Rollback
type RollbackList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Rollback `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Rollback{}, &RollbackList{})
} 