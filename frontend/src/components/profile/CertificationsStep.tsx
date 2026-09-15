"use client";

import React from "react";
import { Certification } from "@/types/profile";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Award, Plus, Trash2 } from "lucide-react";

interface CertificationsStepProps {
  certifications: Certification[];
  onChangeCertifications: (items: Certification[]) => void;
}

export const CertificationsStep: React.FC<CertificationsStepProps> = ({
  certifications,
  onChangeCertifications,
}) => {
  const addCertification = () => {
    onChangeCertifications([
      ...certifications,
      {
        name: "",
        issuer: "",
        issue_date: "",
        credential_id: "",
        credential_url: "",
      },
    ]);
  };

  const updateCertification = (index: number, field: keyof Certification, value: any) => {
    const updated = [...certifications];
    updated[index] = { ...updated[index], [field]: value };
    onChangeCertifications(updated);
  };

  const removeCertification = (index: number) => {
    onChangeCertifications(certifications.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-500" /> Certifications & Credentials
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Add professional certifications, cloud accreditations, or technical licenses.
        </p>
      </div>

      {certifications.length === 0 ? (
        <Card className="p-8 text-center space-y-4 border-dashed border-slate-800 bg-slate-900/30">
          <Award className="w-10 h-10 text-slate-600 mx-auto" />
          <p className="text-sm text-slate-400">No certifications added yet.</p>
          <Button type="button" variant="primary" size="sm" onClick={addCertification}>
            <Plus className="w-4 h-4 mr-2" /> Add First Certification Entry
          </Button>
        </Card>
      ) : (
        <div className="space-y-6">
          {certifications.map((item, idx) => (
            <Card key={idx} className="p-6 space-y-4 relative border-slate-800 bg-slate-900/80">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Award className="w-3.5 h-3.5" /> Certification #{idx + 1}
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeCertification(idx)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Certification Name *"
                  placeholder="e.g. AWS Certified Solutions Architect"
                  value={item.name}
                  onChange={(e) => updateCertification(idx, "name", e.target.value)}
                />
                <Input
                  label="Issuing Organization *"
                  placeholder="e.g. Amazon Web Services"
                  value={item.issuer}
                  onChange={(e) => updateCertification(idx, "issuer", e.target.value)}
                />
                <Input
                  label="Issue Date"
                  type="month"
                  value={item.issue_date || ""}
                  onChange={(e) => updateCertification(idx, "issue_date", e.target.value)}
                />
                <Input
                  label="Credential ID"
                  placeholder="e.g. AWS-12345678"
                  value={item.credential_id || ""}
                  onChange={(e) => updateCertification(idx, "credential_id", e.target.value)}
                />
                <div className="md:col-span-2">
                  <Input
                    label="Credential Validation URL"
                    placeholder="https://credly.com/org/aws/cert/..."
                    value={item.credential_url || ""}
                    onChange={(e) => updateCertification(idx, "credential_url", e.target.value)}
                  />
                </div>
              </div>
            </Card>
          ))}

          <Button type="button" variant="outline" size="sm" onClick={addCertification} className="w-full">
            <Plus className="w-4 h-4 mr-2" /> Add Another Certification
          </Button>
        </div>
      )}
    </div>
  );
};
