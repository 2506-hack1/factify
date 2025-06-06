import React, { useState } from 'react';

export interface TabsProps {
  defaultValue: string;
  children: React.ReactNode;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ defaultValue, children, className = '' }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <div className={`tabs ${className}`} data-active-tab={activeTab}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { 
            activeTab, 
            setActiveTab,
            ...child.props 
          } as any);
        }
        return child;
      })}
    </div>
  );
};

export interface TabsListProps {
  children: React.ReactNode;
  className?: string;
  activeTab?: string;
  setActiveTab?: (value: string) => void;
}

export const TabsList: React.FC<TabsListProps> = ({ 
  children, 
  className = '', 
  activeTab, 
  setActiveTab 
}) => {
  return (
    <div className={`tabs-list ${className}`}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { 
            activeTab, 
            setActiveTab,
            ...child.props 
          } as any);
        }
        return child;
      })}
    </div>
  );
};

export interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  className?: string;
  activeTab?: string;
  setActiveTab?: (value: string) => void;
}

export const TabsTrigger: React.FC<TabsTriggerProps> = ({ 
  value, 
  children, 
  className = '', 
  activeTab, 
  setActiveTab 
}) => {
  const isActive = activeTab === value;
  
  return (
    <button
      className={`tabs-trigger ${className}`}
      data-state={isActive ? 'active' : 'inactive'}
      onClick={() => setActiveTab?.(value)}
    >
      {children}
    </button>
  );
};

export interface TabsContentProps {
  value: string;
  children: React.ReactNode;
  className?: string;
  activeTab?: string;
}

export const TabsContent: React.FC<TabsContentProps> = ({ 
  value, 
  children, 
  className = '', 
  activeTab 
}) => {
  if (activeTab !== value) {
    return null;
  }
  
  return (
    <div className={`tabs-content ${className}`}>
      {children}
    </div>
  );
};
