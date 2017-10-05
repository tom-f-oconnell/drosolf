function [iPN_homo] = PNtransform(ORNc)
% ORNc is the raw Hallem ORN matrix

% compute the EAG based on raw Hallem ORN values
HI = sum(ORNc,2);    %HI = hallem index (176x1 mat)
numstim=length(HI);
EAG = HI/190;
k = find(EAG<0);
EAG(k) = 0;
for i=1:size(ORNc,2)
    EAG(:,i)=EAG(:,1); %duplicate EAG into 23 columns
end


% parameters for transformation
rmax = 165;
n = 1.5;
sigma = 12;

m_muhat_deriv=11.24;
m_sigmahat_deriv=5.43;

% set negative ORN values to zero
ORN=ORNc;       %ORN is ORN data with negative values zeroed out
k = find(ORN<0);
ORN(k) = 0;

% no inhibition
niPN = rmax*(ORN.^n)./((ORN.^n)+sigma^n);

% input gain, homogeneous, set at VM7 levels from integration study
m_inp = 10.63;
iPN_homo = rmax*(ORN.^n)./((ORN.^n)+sigma^n+(m_inp*EAG).^n);

%   response gain
m_rs = 0.164;
rPN = 1./((m_rs.*EAG).^n+1).*rmax.*(ORN.^n)./((ORN.^n)+sigma^n);

%input gain, heterogeneous, m values drawn from experimentally determined
%distibution
m_rand = m_muhat_deriv + m_sigmahat_deriv .* randn(100,1);  %generate 100 values of m, drawn from a normal distribution with mean muhat_deriv and SD sigmahat_deriv

m_samp=[];  %holds simulated values of m that are >= 0
for w=1:100 
    if m_rand(w)>=0
        m_samp=cat(1,m_samp, m_rand(w));  %add to m_samp only simulated m values that are >=0
    end
end

for j=1:size(ORNc,2)  %for each glom
    for i=1:numstim  %for each stimulus
        iPN_het(i,j) = rmax * (((ORN(i,j))^n)/(((ORN(i,j))^n) + sigma^n + (m_samp(j)*EAG(i)).^n));
    end
end

end
        

